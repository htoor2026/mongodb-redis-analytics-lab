"""Import a bounded selection of NYC TLC Parquet rows into MongoDB."""

import argparse
import os
from pathlib import Path

import pandas as pd


COLUMNS = [
    "tpep_pickup_datetime",
    "tpep_dropoff_datetime",
    "PULocationID",
    "DOLocationID",
    "passenger_count",
    "trip_distance",
    "fare_amount",
    "total_amount",
    "payment_type",
]


def positive_int(value):
    number = int(value)
    if number < 1:
        raise argparse.ArgumentTypeError("must be a positive integer")
    return number


def load_records(path, limit):
    frame = pd.read_parquet(path)
    missing = sorted(set(COLUMNS) - set(frame.columns))
    if missing:
        raise ValueError(f"Missing required columns: {', '.join(missing)}")
    frame = frame.loc[:, COLUMNS].head(limit).copy()
    for column in ("tpep_pickup_datetime", "tpep_dropoff_datetime"):
        frame[column] = pd.to_datetime(frame[column], errors="raise")
    # Object dtype prevents numeric columns from turning None back into NaN.
    frame = frame.astype(object).where(pd.notnull(frame), None)
    records = frame.to_dict(orient="records")
    return [
        {
            key: value.to_pydatetime() if isinstance(value, pd.Timestamp) else value
            for key, value in record.items()
        }
        for record in records
    ]


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--file", type=Path, default=Path("yellow_tripdata_2024-09.parquet"))
    parser.add_argument("--limit", type=positive_int, default=200_000)
    parser.add_argument("--batch-size", type=positive_int, default=1_000)
    args = parser.parse_args()

    uri = os.environ.get("MONGODB_URI")
    if not uri:
        parser.error("Set MONGODB_URI to your MongoDB connection URI.")
    if not args.file.is_file():
        parser.error(f"Parquet file not found: {args.file}")

    from pymongo import MongoClient

    records = load_records(args.file, args.limit)
    if not records:
        print("No rows to import.")
        return

    database = os.environ.get("MONGODB_DATABASE", "global_lab")
    collection = os.environ.get("MONGODB_COLLECTION", "tlc_trips")
    with MongoClient(uri, serverSelectionTimeoutMS=10_000) as client:
        client.admin.command("ping")
        target = client[database][collection]
        print(f"Importing {len(records):,} rows into {database}.{collection}...")
        for start in range(0, len(records), args.batch_size):
            target.insert_many(records[start : start + args.batch_size])
    print("TLC import completed successfully.")


if __name__ == "__main__":
    main()
