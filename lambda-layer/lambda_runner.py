"""
Lambda function to retrieve tile locations and upload data to s3
"""

import os
import asyncio
import csv
import time
import boto3
import io
from io import StringIO
from aiohttp import ClientSession
from pytile import async_login


TILE_EMAIL = os.getenv("TILE_EMAIL", "")
TILE_PASSWORD = os.getenv("TILE_PASSWORD", "")
BUCKET_NAME = os.getenv("BUCKET_NAME", "")
BUCKET_PREFIX = "tile-tracker/data"
NOW = time.gmtime()


async def retrieve_data():
    async with ClientSession() as session:
        api = await async_login(TILE_EMAIL, TILE_PASSWORD, session)
        tiles = await api.async_get_tiles()
        return tiles


def lambda_handler(event, context):
    tiles = asyncio.run(retrieve_data())
    data = []
    for tile in tiles.values():
        data.append(
            {
                "uuid": tile.uuid,
                "name": tile.name,
                "latitude": tile.latitude,
                "longitude": tile.longitude,
                "last_timestamp_utc": tile.last_timestamp,
                "retrieved_at_utc": time.strftime("%Y-%m-%d %H:%M:%S", NOW),
            }
        )
    print("%s tiles retrieved." % (len(tiles)))

    if not data:
        print("No tiles. Exiting")
        return

    csv_content = StringIO()
    writer = csv.DictWriter(csv_content, fieldnames=data[0].keys())
    writer.writeheader()
    writer.writerows(data)
    csv_content.seek(0)

    s3 = boto3.client("s3")
    fn = time.strftime("%Y%m%d%H%M%S", NOW) + ".csv"
    s3_key = BUCKET_PREFIX + "/" + fn
    s3.upload_fileobj(
        io.BytesIO(csv_content.getvalue().encode("utf-8")), BUCKET_NAME, s3_key
    )
    print("Data uploaded. Done.")
    return
