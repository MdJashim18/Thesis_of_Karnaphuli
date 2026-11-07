import os
import pandas as pd
from influxdb_client import InfluxDBClient

from config import INFLUXDB_URL, INFLUXDB_TOKEN, INFLUXDB_ORG


def export_data():

    print("DAY 26: INFLUXDB DATA EXPORT")
    print("-" * 50)

    client = InfluxDBClient(
        url=INFLUXDB_URL,
        token=INFLUXDB_TOKEN,
        org=INFLUXDB_ORG
    )

    try:
        query_api = client.query_api()

        query = '''
        from(bucket: "tunnel_telemetry")
          |> range(start: -1h)
        '''

        print("Connecting to InfluxDB...")
        print("Querying the last 1 hour of telemetry data...")

        result = query_api.query_data_frame(
            query=query,
            org=INFLUXDB_ORG
        )

        # InfluxDB may return one DataFrame or a list of DataFrames.
        if isinstance(result, list):
            frames = [frame for frame in result if not frame.empty]

            if frames:
                df = pd.concat(frames, ignore_index=True)
            else:
                df = pd.DataFrame()

        else:
            df = result

        if df.empty:
            print("WARNING: No telemetry data found in the last 1 hour.")
            print("CSV export was not created.")
            return

        # Create output directory if it does not exist.
        output_dir = os.path.join("data", "cleaned")
        os.makedirs(output_dir, exist_ok=True)

        output_file = os.path.join(
            output_dir,
            "month2_final_dataset.csv"
        )

        # Export data to CSV.
        df.to_csv(output_file, index=False)

        print("\nExport successful!")
        print("Total records:", len(df))
        print("Total columns:", len(df.columns))
        print("Output file:", output_file)

        print("\nExported columns:")
        print(list(df.columns))

    except Exception as e:
        print("\nERROR: Data export failed.")
        print("Details:", e)

    finally:
        client.close()


if __name__ == "__main__":
    export_data()