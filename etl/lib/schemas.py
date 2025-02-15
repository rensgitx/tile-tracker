"""
Column names and types for the TileSegment table
"""

# Specs for reading raw files with pd.read_csv
spec_dtypes = {
    "uuid": str,
    "name": str,
    "latitude": "float64",
    "longitude": "float64",
}

spec_dates = ["last_timestamp_utc", "retrieved_at_utc"]

# TileSegment columns
final_columns = [
    "uuid",
    "name",
    "latitude",
    "longitude",
    "segment",
    "state",
    "start_segment",
    "last_timestamp_utc",
    "retrieved_at_utc",
]
