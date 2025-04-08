#! python

"""
Process 1 day of data
"""

import pandas as pd
from sqlalchemy import create_engine, text, Table, MetaData
from sqlalchemy.engine import Engine

from .schemas import spec_dtypes, spec_dates, final_columns
from .state import State
import logging

from pathlib import Path
import click
import os
import re
from typing import Optional
from datetime import datetime, timezone


logger = logging.getLogger(__name__)


@click.command()
@click.argument("filedate")
@click.option(
    "--srcdir",
    default="",
    help="Local directory to search for the raw files. If omitted, retrieve files from the dedicated s3 location.",
)
@click.option(
    "--outdir",
    default="",
    help="Local directory to output the data as a csv file. If omitted, insert the data into the dedicated db.",
)
def run(filedate: str, srcdir: str = "", outdir: str = ""):
    """
    Run the workflow to process 1 day of data

    Retrieve all files with <filedate> prefix, transform and insert the data to db, where <filedate> is in YYYYMMDD format.
    Usage example:
    python lib/process1d.py 20250202 --srcdir='data/input' --outdir='data/output'
    """
    assert re.search(
        "[0-9]{8}", filedate
    ), f"filedate '{filedate}' is not in a valid format!"

    logger.info(f"Loading raw files from {'s3' if not srcdir else srcdir}")
    if srcdir:
        df = retrieve_local_files(filedate, srcdir)
    else:
        BUCKET_NAME = os.getenv("BUCKET_NAME")
        KEY_PREFIX = os.getenv("KEY_PREFIX")
        df = retrieve_from_s3(filedate, BUCKET_NAME, KEY_PREFIX)

    len_df = df.shape[0]
    logger.info(f"{len_df} records loaded.")

    if len_df == 0:
        logger.info("No records to transform. Exiting.")
        return

    dburl = f"sqlite:///{os.getenv('DB_NAME')}"
    logger.info(f"Connecting to db: {dburl}")
    engine = create_engine(dburl, echo=True)

    # Table to modify
    metadata = MetaData()
    table = Table("trackapp_tilesegment", metadata, autoload_with=engine)

    logger.info("Start transformation.")
    df = transform(df, engine, table)
    logger.info(f"Transform complete. Num records: {df.shape[0]}")

    if outdir:
        fp_out = Path(outdir, f"out_{filedate}.csv")
        df.to_csv(fp_out, index=False)
        logger.info(
            f"Saving result to a csv file since --outdir flag is on: {fp_out}.\n"
            + "Exiting successfully."
        )
        return

    logger.info(f"Inserting records to {table.name}")
    upsert(df, engine, table)
    logger.info(f"Completed inserting records. {df.shape[0]} records inserted")


def retrieve_from_s3(filedate: str, bucket_name: str, prefix: str) -> pd.DataFrame:
    """
    Retrieve all csv files from s3

    Files are prefixed like s3://{bucket_name}/{key_prefix}/{filedate}
    """
    # TO DO
    return pd.DataFrame(columns=spec_dtypes.keys())


def retrieve_local_files(filedate: str, srcdir: str) -> pd.DataFrame:
    """
    Retrieve files from localdir

    Search for files in <srcdir> that are prefixed with <filedate> and load the data into a pandas df. <filedate> must be in YYYYMMDD format.
    """
    files = [
        Path(srcdir, fn)
        for fn in os.listdir(srcdir)
        if fn.startswith(filedate) and fn.endswith(".csv")
    ]
    df = pd.concat(
        [
            pd.read_csv(
                fp,
                dtype=spec_dtypes,
                parse_dates=spec_dates,
                date_format="ISO8601",
                na_filter=False,
            )
            for fp in files
        ],
        ignore_index=True,
    )
    return df


def classify_state(
    lat2_diff: Optional[float], lon2_diff: Optional[float]
) -> Optional[str]:
    """
    Returns a state based on lat/lon diff between 2 consecutive samples
    """
    if pd.isnull(lat2_diff) or pd.isnull(lon2_diff):
        return State.PENDING.value
    if lat2_diff != 0 or lon2_diff != 0:
        return State.UNSETTLE.value
    return State.SETTLE.value


def transform(df: pd.DataFrame, engine: Optional[Engine] = None, table: Optional[Table] = None) -> pd.DataFrame:
    """
    Segment the location data

    Divide the location into segments, classify the state of each segment and
    get the start time of each segment. To classify the state of the first segment,
    we retrieve the latest segment from the previous day from the db.
    If engine is None, skip this step, leave state as pending and start_segment=None
    """

    # Round latitude and longitude to 2 decimal points (roughly 1 km tolerance)
    df[["lat2", "lon2"]] = df[["latitude", "longitude"]].round(2)

    df.sort_values(by=["uuid", "retrieved_at_utc"], ignore_index=True, inplace=True)
    df.drop_duplicates(
        subset=["uuid", "lat2", "lon2", "last_timestamp_utc"],
        keep="first",
        inplace=True,
        ignore_index=True,
    )

    # Columns to add: state, segment, start_segment
    for uuid, group in df.groupby(by="uuid"):
        df.drop(group.index, inplace=True)
        group = transform_group(group, engine, table)
        df = pd.concat([df, group])

    # Drop helper columns and reset index
    df.drop(columns=["lat2", "lon2"], inplace=True)
    df.reset_index(inplace=True)

    # Reorder columns for ease of observation
    df = df[final_columns]
    df["state"] = df["state"].map(lambda x: str(x))

    return df


def transform_group(
    group: pd.DataFrame, engine: Optional[Engine] = None, table: Optional[Table] = None
) -> pd.DataFrame:
    """
    Adds these columns to the input df: 'segment', 'state', 'start_segment'
    """
    if group.shape[0] == 1:
        group["segment"] = 1
        group["state"] = State.PENDING.value
        group["start_segment"] = None
        return group

    helper_columns = [
        "lat2_diff",
        "lon2_diff",
        "state_change",
        "last_timestamp_utc_prev",
    ]
    group[["lat2_diff", "lon2_diff"]] = group[["lat2", "lon2"]].diff()
    group["state"] = group.apply(
        lambda row: classify_state(row.lat2_diff, row.lon2_diff), axis=1
    )
    group["state_change"] = group["state"] != group["state"].shift(1)
    group["segment"] = group["state_change"].cumsum()
    group["last_timestamp_utc_prev"] = group["last_timestamp_utc"].shift(1)
    start_segment_df = (
        group.groupby("segment")["last_timestamp_utc_prev"]
        .first()
        .to_frame()
        .rename(columns={"last_timestamp_utc_prev": "start_segment"})
    )
    group = pd.merge(group, start_segment_df, how="left", on="segment")

    # for each segment, keep only the last record if state is settle
    # since there is no change in location since start_segment
    settle_df = group[group.state == State.SETTLE.value].copy()

    # Drop the records from group. Will re-insert from settle_df
    group.drop(settle_df.index, inplace=True)

    settle_df.drop_duplicates(subset=["segment"], keep="last", inplace=True)

    group = pd.concat([group, settle_df])
    group.sort_values(
        by=["segment", "start_segment", "last_timestamp_utc"], inplace=True
    )

    # drop helper columns
    group.drop(columns=helper_columns, inplace=True)

    if engine:
        last_timestamp = group.iloc[0]["last_timestamp_utc"]
        uuid = group.iloc[0]["uuid"]
        df_prev = get_prev_from_db(uuid, last_timestamp, engine, table)

        # if df_prev has no record, skip classifying the state (keep as State.PENDING)
        if not df_prev.empty:
            group.at[0, "start_segment"] = pd.to_datetime(
                df_prev.iloc[0]["last_timestamp_utc"]
            )
            if (group.iloc[0].lat2 == round(df_prev.iloc[0]["latitude"], 2)) and (
                group.iloc[0].lon2 == round(df_prev.iloc[0]["longitude"], 2)
            ):
                group.at[0, "state"] = State.SETTLE.value
            else:
                group.at[0, "state"] = State.UNSETTLE.value
    return group


def get_prev_from_db(
    uuid: str, last_timestamp_utc: datetime, engine: Engine, table: Table
) -> pd.DataFrame:
    query = f"""
    SELECT last_timestamp_utc, latitude, longitude
    FROM {table.name}
    WHERE uuid='{uuid}'
        AND last_timestamp_utc > DATE('{last_timestamp_utc.strftime("%Y-%m-%d")}', '-3 day')
        AND last_timestamp_utc <= DATE('{last_timestamp_utc.strftime("%Y-%m-%d")}')
    ORDER BY last_timestamp_utc desc
    LIMIT 1
    """
    df = pd.read_sql(query, engine)
    return df


def upsert(df: pd.DataFrame, engine: Engine, table: Table):
    if df.shape[0] < 1:
        return
    df["updated_at"] = datetime.now(timezone.utc)
    # convert NaT to None since sqlalchemy does not do the conversion
    df["start_segment"] = (
        df["start_segment"].astype(object).where(df["start_segment"].notnull(), None)
    )
    # convert all date columns to str since sqlalchemy does not handle Timestamp
    date_columns = [
        "start_segment",
        "last_timestamp_utc",
        "retrieved_at_utc",
        "updated_at",
    ]
    for dtcol in date_columns:
        df[dtcol] = (
            df[dtcol].astype(str).map(lambda x: "" if x in ["NaT", "None"] else x)
        )
    columns = [c.name for c in table.columns if c.name != "id"]
    columns_str = ",".join(columns)
    columns_str2 = ",".join([":" + c for c in columns])
    set_vals_str = ", ".join([f"{col} = excluded.{col}" for col in columns])

    query = text(
        f"""
        INSERT INTO {table.name} ({columns_str})
        VALUES ({columns_str2})
        ON CONFLICT({','.join(['uuid', 'last_timestamp_utc'])})
        DO UPDATE SET
            {set_vals_str};
        """
    )
    with engine.connect() as conn:
        conn.execute(query, df.to_dict(orient="records"))
        conn.commit()


if __name__ == "__main__":
    # pylint: disable = no-value-for-parameter
    run()
