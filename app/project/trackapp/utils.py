from typing import Dict, Any
from datetime import datetime, timezone
from .models import TileSegment


def get_most_recent_location(name: str, is_demo: bool = False) -> Dict[str, Any]:

    if is_demo:
        latitude = 43.6945117  # somewhere in Lake Ontario
        longitude = -79.3068992
        last_seen_utc = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
    else:
        last_seen = (
            TileSegment.objects.filter(name=name)
            .order_by("-last_timestamp_utc")
            .first()
        )
        if not last_seen:
            return {}
        latitude = last_seen.latitude
        longitude = last_seen.longitude
        last_seen_utc = last_seen.last_timestamp_utc

    return {
        "name": f"{name}",
        "latitude": float(latitude),
        "longitude": float(longitude),
        "last_seen_utc": last_seen_utc.strftime("%Y-%m-%d %H:%M+00"),
    }


def clean_segments(tracks: TileSegment, from_time: datetime) -> Dict[str, Any]:
    """
    Concatenate consecutive track segments if no movement and
    calculate final duration of a segment
    """
    segments = []
    for ix, row in enumerate(tracks):
        name = row.name
        latitude = row.latitude
        longitude = row.longitude
        state = row.state
        start_utc = row.start_segment if row.start_segment else from_time
        end_utc = row.last_timestamp_utc

        if (
            not segments
            or state != "Settle"
            or round(latitude, 2) != round(segments[-1]["latitude"], 2)
            or round(longitude, 2) != round(segments[-1]["longitude"], 2)
        ):
            segments.append(
                {
                    "name": name,
                    "latitude": latitude,
                    "longitude": longitude,
                    "state": state,
                    "start_utc": start_utc,
                    "end_utc": end_utc,
                    "duration": "",  # to calculate
                    "segment_order": 1,  # to calculate
                }
            )
        else:
            segments[-1]["end_utc"] = end_utc
            segments[-1]["state"] = state

    for ix, row in enumerate(segments):
        duration_seconds = (row["end_utc"] - row["start_utc"]).total_seconds()
        hours, minutes = divmod(duration_seconds // 60, 60)
        segments[ix]["duration"] = f"{hours}h {minutes}m"
        segments[ix]["segment_order"] = ix + 1

        # Cast values
        segments[ix]["start_utc"] = segments[ix]["start_utc"].strftime(
            "%Y-%m-%d %H:%M+00"
        )
        segments[ix]["end_utc"] = segments[ix]["end_utc"].strftime("%Y-%m-%d %H:%M+00")
    return segments
