
import os
from dotenv import load_dotenv
from influxdb_client import InfluxDBClient, Point, WritePrecision
from influxdb_client.client.write_api import SYNCHRONOUS
from datetime import datetime, timezone

# Load credentials from the project's .env file
load_dotenv()

url = os.getenv("INFLUXDB_URL")
token = os.getenv("INFLUXDB_TOKEN")
org = os.getenv("INFLUXDB_ORG")
bucket = os.getenv("INFLUXDB_BUCKET")

if not all([url, token, org, bucket]):
    raise SystemExit(
        "ERROR: Missing InfluxDB settings. Check your .env file."
    )

try:
    with InfluxDBClient(url=url, token=token, org=org) as client:
        # Write a clearly labelled synthetic connection-test point
        point = (
            Point("influxdb_connection_test")
            .tag("device_id", "ESP32-GW-LAB-001")
            .tag("zone_id", "LAB_PROTOTYPE")
            .tag("test", "true")
            .field("temperature", 28.4)
            .field("humidity", 72.1)
            .time(datetime.now(timezone.utc), WritePrecision.S)
        )

        write_api = client.write_api(write_options=SYNCHRONOUS)
        write_api.write(bucket=bucket, org=org, record=point)
        print("WRITE SUCCESS: Test point sent to InfluxDB.")

        # Query the test measurement back
        query = f'''
        from(bucket: "{bucket}")
          |> range(start: -15m)
          |> filter(fn: (r) => r["_measurement"] == "influxdb_connection_test")
          |> filter(fn: (r) => r["test"] == "true")
          |> last()
        '''

        tables = client.query_api().query(query, org=org)
        rows = [record for table in tables for record in table.records]

        if rows:
            print("READ SUCCESS: Test point retrieved.")
            for record in rows:
                print(f"{record.get_field()}: {record.get_value()}")
        else:
            print("WRITE completed, but no test point was returned.")

except Exception as exc:
    print(f"CONNECTION/TEST FAILED: {type(exc).__name__}: {exc}")
    raise SystemExit(1)
