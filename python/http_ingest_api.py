import os
from datetime import datetime, timezone

from flask import Flask, request, jsonify
from dotenv import load_dotenv
from influxdb_client import InfluxDBClient, Point, WritePrecision

load_dotenv()

INFLUX_URL = os.getenv("INFLUXDB_URL", "http://localhost:8086")
INFLUX_TOKEN = os.getenv("INFLUXDB_TOKEN")
INFLUX_ORG = os.getenv("INFLUXDB_ORG")
INFLUX_BUCKET = os.getenv("INFLUXDB_BUCKET")

if not all([INFLUX_TOKEN, INFLUX_ORG, INFLUX_BUCKET]):
    raise RuntimeError(
        "Check INFLUXDB_TOKEN, INFLUXDB_ORG and INFLUXDB_BUCKET in .env"
    )

app = Flask(__name__)

client = InfluxDBClient(
    url=INFLUX_URL,
    token=INFLUX_TOKEN,
    org=INFLUX_ORG,
)

write_api = client.write_api()


@app.get("/health")
def health():
    return jsonify({
        "status": "online",
        "service": "Karnaphuli SHM HTTP API"
    }), 200


@app.post("/telemetry")
def telemetry():
    data = request.get_json(silent=True)

    if not isinstance(data, dict):
        return jsonify({"error": "Valid JSON body required"}), 400

    required = [
        "device_id", "zone_id", "temperature",
        "humidity", "accel_x", "accel_y", "accel_z",
        "water_raw", "load_raw", "load_kg", "quality_flag"
    ]

    missing = [key for key in required if key not in data]
    if missing:
        return jsonify({
            "error": "Missing required fields",
            "fields": missing
        }), 400

    try:
        point = (
            Point("tunnel_telemetry")
            .tag("device_id", str(data["device_id"]))
            .tag("gateway_id", str(data.get("gateway_id", "unknown")))
            .tag("zone_id", str(data["zone_id"]))
            .tag("quality_flag", str(data["quality_flag"]))
            .field("temperature", float(data["temperature"]))
            .field("humidity", float(data["humidity"]))
            .field("accel_x", float(data["accel_x"]))
            .field("accel_y", float(data["accel_y"]))
            .field("accel_z", float(data["accel_z"]))
            .field("water_raw", int(data["water_raw"]))
            .field("load_raw", int(data["load_raw"]))
            .field("load_kg", float(data["load_kg"]))
            .field("dht_valid", bool(data.get("dht_valid", False)))
            .field("mpu_valid", bool(data.get("mpu_valid", False)))
            .field("hx711_valid", bool(data.get("hx711_valid", False)))
            .time(datetime.now(timezone.utc), WritePrecision.S)
        )

        write_api.write(
            bucket=INFLUX_BUCKET,
            org=INFLUX_ORG,
            record=point
        )

        return jsonify({
            "status": "saved",
            "measurement": "tunnel_telemetry"
        }), 201

    except (ValueError, TypeError) as error:
        return jsonify({"error": f"Invalid sensor value: {error}"}), 400
    except Exception:
        app.logger.exception("InfluxDB write failed")
        return jsonify({"error": "InfluxDB write failed; check server log"}), 500


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, threaded=True, debug=False)