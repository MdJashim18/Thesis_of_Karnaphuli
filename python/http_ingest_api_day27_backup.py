
import os
import json
import math
import threading

from pathlib import Path
from datetime import datetime, timezone

from flask import Flask, request, jsonify
from dotenv import load_dotenv

from influxdb_client import InfluxDBClient, Point, WritePrecision
from influxdb_client.client.write_api import SYNCHRONOUS


load_dotenv()

# ================= CONFIG =================

BASE_DIR = Path(__file__).resolve().parent

DATA_DIR = BASE_DIR / "data" / "raw"
DATA_DIR.mkdir(parents=True, exist_ok=True)

CONTINUOUS_LOG_FILE = DATA_DIR / "continuous_24h.jsonl"
RELIABILITY_LOG_FILE = DATA_DIR / "reliability_log.jsonl"

INFLUX_URL = os.getenv("INFLUXDB_URL", "http://localhost:8086")
INFLUX_TOKEN = os.getenv("INFLUXDB_TOKEN")
INFLUX_ORG = os.getenv("INFLUXDB_ORG")
INFLUX_BUCKET = os.getenv("INFLUXDB_BUCKET")

if not all([INFLUX_TOKEN, INFLUX_ORG, INFLUX_BUCKET]):
    raise RuntimeError("Check InfluxDB .env configuration")


app = Flask(__name__)

client = InfluxDBClient(
    url=INFLUX_URL,
    token=INFLUX_TOKEN,
    org=INFLUX_ORG
)

write_api = client.write_api(write_options=SYNCHRONOUS)

lock = threading.Lock()


# ================= SESSION =================

session = {
    "active": False,
    "session_id": None,
    "start_time": None,
    "stop_time": None,
    "interval_ms": 1000
}


# ================= JSONL LOGGER =================

def append_jsonl(file_path, record):

    with open(file_path, "a", encoding="utf-8") as file:

        file.write(
            json.dumps(
                record,
                ensure_ascii=False,
                allow_nan=False
            ) + "\n"
        )

        file.flush()
        os.fsync(file.fileno())


# ================= HEALTH =================

@app.get("/health")
def health():

    return jsonify({
        "status": "online",
        "service": "Karnaphuli SHM HTTP API",
        "continuous_logger": True,
        "continuous_log_file": str(CONTINUOUS_LOG_FILE),
        "reliability_log_file": str(RELIABILITY_LOG_FILE)
    }), 200


# ================= START SESSION =================

@app.post("/session/start")
def start_session():

    global session

    data = request.get_json(silent=True) or {}

    session_id = data.get("session_id", "SHM-DAY27-001")

    try:
        interval_ms = int(data.get("interval_ms", 1000))
    except (ValueError, TypeError):
        return jsonify({"error": "Invalid interval"}), 400

    if interval_ms <= 0:
        return jsonify({"error": "Invalid interval"}), 400

    with lock:

        if session["active"]:
            return jsonify({
                "error": "A collection session is already active"
            }), 409

        session = {
            "active": True,
            "session_id": str(session_id),
            "start_time": datetime.now(timezone.utc),
            "stop_time": None,
            "interval_ms": interval_ms
        }

        start_time = session["start_time"]

    app.logger.info("Collection started: %s", session_id)

    return jsonify({
        "status": "collection_started",
        "session_id": session_id,
        "interval_ms": interval_ms,
        "start_time": start_time.isoformat(),
        "continuous_logging": True
    }), 200


# ================= TELEMETRY =================

@app.post("/telemetry")
def telemetry():

    data = request.get_json(silent=True)

    if not isinstance(data, dict):
        return jsonify({"error": "Valid JSON required"}), 400

    required = [
        "device_id", "zone_id", "temperature",
        "humidity", "accel_x", "accel_y", "accel_z",
        "water_raw", "load_raw", "load_kg",
        "quality_flag", "sequence_number",
        "device_timestamp_ms", "wifi_reconnect_count"
    ]

    missing = [key for key in required if key not in data]

    if missing:
        return jsonify({
            "error": "Missing fields",
            "fields": missing
        }), 400

    try:

        with lock:

            if not session["active"]:
                return jsonify({
                    "error": "No active collection session"
                }), 409

            if str(data.get("session_id")) != session["session_id"]:
                return jsonify({
                    "error": "Session ID mismatch"
                }), 409

            sequence = int(data["sequence_number"])

            if sequence < 0:
                return jsonify({"error": "Invalid sequence"}), 400

            received_at = datetime.now(timezone.utc)

            device_timestamp_ms = int(data["device_timestamp_ms"])

            latency_ms = (
                received_at.timestamp() * 1000
                - device_timestamp_ms
            )

            latency_valid = (
                device_timestamp_ms > 0
                and 0 <= latency_ms <= 60000
            )

            # Validate numerical sensor values

            temperature = float(data["temperature"])
            humidity = float(data["humidity"])

            accel_x = float(data["accel_x"])
            accel_y = float(data["accel_y"])
            accel_z = float(data["accel_z"])

            water_raw = int(data["water_raw"])
            load_raw = int(data["load_raw"])
            load_kg = float(data["load_kg"])

            numeric_values = [
                temperature, humidity,
                accel_x, accel_y, accel_z,
                load_kg, latency_ms
            ]

            if not all(math.isfinite(v) for v in numeric_values):
                return jsonify({
                    "error": "Non-finite sensor value"
                }), 400

            reconnect_count = int(data["wifi_reconnect_count"])

            # ================= INFLUXDB =================

            point = (
                Point("tunnel_telemetry")

                .tag("device_id", str(data["device_id"]))
                .tag("gateway_id", str(data.get("gateway_id", "unknown")))
                .tag("zone_id", str(data["zone_id"]))
                .tag("quality_flag", str(data["quality_flag"]))

                .field("temperature", temperature)
                .field("humidity", humidity)

                .field("accel_x", accel_x)
                .field("accel_y", accel_y)
                .field("accel_z", accel_z)

                .field("water_raw", water_raw)
                .field("load_raw", load_raw)
                .field("load_kg", load_kg)

                .field("sequence_number", sequence)
                .field("wifi_reconnect_count", reconnect_count)

                .field("latency_ms", float(latency_ms))
                .field("latency_valid", latency_valid)

                .field("dht_valid", bool(data.get("dht_valid", False)))
                .field("mpu_valid", bool(data.get("mpu_valid", False)))
                .field("hx711_valid", bool(data.get("hx711_valid", False)))

                .time(received_at, WritePrecision.NS)
            )

            # Save to InfluxDB first

            write_api.write(
                bucket=INFLUX_BUCKET,
                org=INFLUX_ORG,
                record=point
            )

            # ================= FULL SENSOR JSONL =================

            continuous_record = dict(data)

            continuous_record.update({
                "session_id": session["session_id"],
                "sequence_number": sequence,
                "received_at": received_at.isoformat(),
                "device_timestamp_ms": device_timestamp_ms,
                "latency_ms": round(latency_ms, 3),
                "latency_valid": latency_valid,
                "wifi_reconnect_count": reconnect_count
            })

            append_jsonl(
                CONTINUOUS_LOG_FILE,
                continuous_record
            )

            # ================= RELIABILITY JSONL =================

            reliability_record = {
                "session_id": session["session_id"],
                "sequence_number": sequence,
                "received_at": received_at.isoformat(),
                "device_timestamp_ms": device_timestamp_ms,
                "latency_ms": round(latency_ms, 3),
                "latency_valid": latency_valid,
                "wifi_reconnect_count": reconnect_count
            }

            append_jsonl(
                RELIABILITY_LOG_FILE,
                reliability_record
            )

        return jsonify({
            "status": "saved",
            "sequence_number": sequence,
            "timestamp_utc": received_at.isoformat(),
            "latency_ms": round(latency_ms, 3),
            "latency_valid": latency_valid,
            "influxdb_saved": True,
            "continuous_jsonl_saved": True,
            "reliability_jsonl_saved": True
        }), 201

    except (ValueError, TypeError, OverflowError) as error:

        return jsonify({
            "error": f"Invalid sensor value: {error}"
        }), 400

    except Exception:

        app.logger.exception("Telemetry storage failed")

        return jsonify({
            "error": "Data storage failed"
        }), 500


# ================= STOP SESSION =================

@app.post("/session/stop")
def stop_session():

    global session

    with lock:

        if not session["active"]:
            return jsonify({
                "error": "No active session"
            }), 409

        session["stop_time"] = datetime.now(timezone.utc)
        session["active"] = False

        stopped_id = session["session_id"]
        stopped_time = session["stop_time"]

    return jsonify({
        "status": "collection_stopped",
        "session_id": stopped_id,
        "stop_time": stopped_time.isoformat()
    }), 200


# ================= RELIABILITY SUMMARY =================

@app.get("/reliability/summary")
def reliability_summary():

    with lock:

        if session["stop_time"] is None:
            return jsonify({
                "error": "Stop the collection session first"
            }), 409

        current_session = session.copy()

    start = current_session["start_time"]
    stop = current_session["stop_time"]

    duration = (stop - start).total_seconds()

    interval_ms = current_session["interval_ms"]

    expected = math.floor(
        duration * 1000 / interval_ms
    ) + 1

    records = []

    if RELIABILITY_LOG_FILE.exists():

        with open(RELIABILITY_LOG_FILE, "r", encoding="utf-8") as file:

            for line in file:

                try:
                    item = json.loads(line)

                    if item["session_id"] == current_session["session_id"]:
                        records.append(item)

                except (json.JSONDecodeError, KeyError):
                    continue

    sequences = set(
        item["sequence_number"] for item in records
    )

    received = len(sequences)

    missing = max(0, expected - received)

    duplicate_count = len(records) - received

    latencies = [
        item["latency_ms"]
        for item in records
        if item["latency_valid"]
    ]

    average_latency = (
        sum(latencies) / len(latencies)
        if latencies else None
    )

    maximum_latency = (
        max(latencies)
        if latencies else None
    )

    reconnect_values = [
        item["wifi_reconnect_count"]
        for item in records
    ]

    reconnection_events = (
        max(reconnect_values) - min(reconnect_values)
        if reconnect_values else 0
    )

    report = {
        "session_id": current_session["session_id"],
        "collection_start": start.isoformat(),
        "collection_end": stop.isoformat(),

        "total_expected_readings": expected,
        "total_received_readings": received,
        "missing_readings": missing,
        "duplicate_readings": duplicate_count,

        "average_latency_ms": (
            round(average_latency, 3)
            if average_latency is not None else None
        ),

        "maximum_latency_ms": (
            round(maximum_latency, 3)
            if maximum_latency is not None else None
        ),

        "valid_latency_samples": len(latencies),

        "reconnection_events": reconnection_events,

        "data_collection_duration_seconds": round(duration, 3),

        "data_collection_duration_minutes": round(
            duration / 60, 3
        ),

        "collection_interval_ms": interval_ms
    }

    return jsonify(report), 200


# ================= RUN =================

if __name__ == "__main__":

    app.run(
        host="0.0.0.0",
        port=5000,
        threaded=True,
        debug=False
    )
