
from pathlib import Path
import os

import pandas as pd
from dotenv import load_dotenv
from influxdb_client import InfluxDBClient


# ==================================================
# PROJECT CONFIGURATION
# ==================================================

PROJECT_ROOT = Path(__file__).resolve().parent.parent
ENV_FILE = PROJECT_ROOT / ".env"
OUTPUT_FILE = PROJECT_ROOT / "python" / "validated_data.csv"

load_dotenv(ENV_FILE, override=True)

INFLUX_URL = os.getenv("INFLUXDB_URL")
INFLUX_TOKEN = os.getenv("INFLUXDB_TOKEN")
INFLUX_ORG = os.getenv("INFLUXDB_ORG")
INFLUX_BUCKET = os.getenv("INFLUXDB_BUCKET")


# ==================================================
# DATA VALIDATION
# ==================================================

def validate_data(df):
    """
    Retain records with recognized quality flags.
    Preserve partial/degraded labels instead of falsely
    marking these records as valid.
    """

    if df.empty:
        return df.copy()

    if "quality_flag" not in df.columns:
        raise ValueError(
            "quality_flag column not found in InfluxDB data."
        )

    result_df = df.copy()

    result_df["quality_flag"] = (
        result_df["quality_flag"]
        .astype("string")
        .str.strip()
        .str.lower()
    )

    recognized_flags = ["valid", "partial", "degraded"]

    result_df = result_df[
        result_df["quality_flag"].isin(recognized_flags)
    ].copy()

    return result_df


# ==================================================
# MAIN
# ==================================================

def main():

    # Check configuration
    settings = {
        "INFLUXDB_URL": INFLUX_URL,
        "INFLUXDB_TOKEN": INFLUX_TOKEN,
        "INFLUXDB_ORG": INFLUX_ORG,
        "INFLUXDB_BUCKET": INFLUX_BUCKET,
    }

    missing = [
        key for key, value in settings.items()
        if not value
    ]

    if missing:
        raise ValueError(
            "Missing .env settings: " + ", ".join(missing)
        )

    # Query recent telemetry
    query = f'''
    from(bucket: "{INFLUX_BUCKET}")
        |> range(start: -1h)
        |> pivot(
            rowKey: ["_time"],
            columnKey: ["_field"],
            valueColumn: "_value"
        )
    '''

    print("Connecting to InfluxDB...")

    with InfluxDBClient(
        url=INFLUX_URL,
        token=INFLUX_TOKEN,
        org=INFLUX_ORG
    ) as client:

        query_api = client.query_api()
        query_result = query_api.query_data_frame(query)

    # Convert query result to one DataFrame
    if isinstance(query_result, pd.DataFrame):
        df = query_result.copy()

    elif isinstance(query_result, list):
        frames = [
            item for item in query_result
            if isinstance(item, pd.DataFrame) and not item.empty
        ]

        if frames:
            df = pd.concat(frames, ignore_index=True)
        else:
            df = pd.DataFrame()

    else:
        df = pd.DataFrame()

    # Remove InfluxDB result/table metadata columns
    metadata = [
        column for column in ["result", "table"]
        if column in df.columns
    ]

    if metadata:
        df.drop(columns=metadata, inplace=True)

    print("\n========== QUERY SUMMARY ==========")
    print("Rows retrieved:", len(df))
    print("Columns:", df.columns.tolist())

    if df.empty:
        print("No data returned for the last hour.")
        print("Check that InfluxDB contains recent telemetry.")
        return

    # Show quality flags before filtering
    print("\n========== QUALITY FLAGS ==========")

    if "quality_flag" in df.columns:
        print(
            df["quality_flag"].value_counts(dropna=False).to_string()
        )
    else:
        raise ValueError(
            "quality_flag is missing. CSV export stopped."
        )

    print("\n========== MISSING VALUES ==========")
    print(df.isna().sum().to_string())

    # Validate according to recognized flags
    output_df = validate_data(df)

    print("\n========== VALIDATION SUMMARY ==========")
    print("Rows retrieved:", len(df))
    print("Rows retained:", len(output_df))
    print("Rows excluded:", len(df) - len(output_df))

    print("\nRetained quality flags:")
    if not output_df.empty:
        print(
            output_df["quality_flag"]
            .value_counts(dropna=False)
            .to_string()
        )

    # Create output directory
    OUTPUT_FILE.parent.mkdir(parents=True, exist_ok=True)

    # Export CSV
    output_df.to_csv(
        OUTPUT_FILE,
        index=False,
        encoding="utf-8-sig"
    )

    print("\n========== CSV EXPORT ==========")
    print("Saved to:", OUTPUT_FILE)
    print("File exists:", OUTPUT_FILE.exists())
    print("File size (bytes):", OUTPUT_FILE.stat().st_size)

    # Read saved CSV back to verify the export
    saved_df = pd.read_csv(OUTPUT_FILE)

    print("\n========== CSV VERIFICATION ==========")
    print("Rows saved in CSV:", len(saved_df))
    print("Columns saved:", len(saved_df.columns))

    if saved_df.empty:
        print(
            "WARNING: CSV contains headers but no data rows. "
            "Review the query and validation results."
        )
    else:
        print("\nFirst five saved records:")
        print(saved_df.head(5).to_string(index=False))
        print("\nCSV export verification successful.")

    # Important: retained records are not necessarily
    # fully valid sensor measurements.
    if "quality_flag" in saved_df.columns:
        if (saved_df["quality_flag"] == "valid").sum() == 0:
            print(
                "\nNOTE: No records have a 'valid' quality flag. "
                "Retained partial/degraded records are preserved "
                "with their original labels."
            )


if __name__ == "__main__":
    main()
