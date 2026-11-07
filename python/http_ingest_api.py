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


# =====================================================
# 1. PATH CONFIGURATION
# =====================================================

BASE_DIR = Path(__file__).resolve().parent.parent

DATA_DIR = BASE_DIR / "data" / "raw"
DATA_DIR.mkdir(parents=True, exist_ok=True)

CONTINUOUS_LOG_FILE = DATA_DIR / "continuous_24h.jsonl"
RELIABILITY_LOG_FILE = DATA_DIR / "reliability_log.jsonl"


# =====================================================
# 2. ENVIRONMENT CONFIGURATION
# =====================================================

load_dotenv(BASE_DIR / ".env")

INFLUXDB_URL = os.getenv("INFLUXDB_URL")
INFLUXDB_TOKEN = os.getenv("INFLUXDB_TOKEN")
INFLUXDB_ORG = os.getenv("INFLUXDB_ORG")
INFLUXDB_BUCKET = os.getenv("INFLUXDB_BUCKET")

if not all([INFLUXDB_URL, INFLUXDB_TOKEN, INFLUXDB_ORG, INFLUXDB_BUCKET]):
    raise RuntimeError("InfluxDB configuration missing in .env")


# =====================================================
# 3. FLASK AND INFLUXDB
# =====================================================

app = Flask(__name__)

influx_client = InfluxDBClient(
    url=INFLUXDB_URL,
    token=INFLUXDB_TOKEN,
    org=INFLUXDB_ORG
)

write_api = influx_client.write_api(
    write_options=SYNCHRONOUS
)

lock = threading.Lock()


# =====================================================
# 4. SESSION CONFIGURATION
# =====================================================

session = {
    "active": False,
    "session_id": None,
    "start_time": None,
    "stop_time": None,
    "interval_ms": 1000
}


# =====================================================
# 5. JSONL APPEND FUNCTION
# =====================================================

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


# =====================================================
# 6. HEALTH CHECK
# =====================================================

@app.route("/health", methods=["GET"])
def health():

    return jsonify({
        "status": "running",
        "session_active": session["active"],
        "session_id": session["session_id"],
        "continuous_log": str(CONTINUOUS_LOG_FILE),
        "reliability_log": str(RELIABILITY_LOG_FILE)
    }), 200


# =====================================================
# 7. START SESSION
# =====================================================

@app.route("/session/start", methods=["POST"])
def start_session():

    data = request.get_json(silent=True) or {}

    with lock:

        if session["active"]:
            return jsonify({
                "error": "A session is already active"
            }), 409

        session["active"] = True

        session["session_id"] = data.get(
            "session_id",
            "SHM-DAY27-001"
        )

        session["start_time"] = datetime.now(
            timezone.utc
        )

        session["stop_time"] = None

        session["interval_ms"] = int(
            data.get("interval_ms", 1000)
        )

        if session["interval_ms"] <= 0:
            session["active"] = False
            return jsonify({"error": "Invalid interval_ms"}), 400

    return jsonify({
        "message": "Session started",
        "session_id": session["session_id"],
        "interval_ms": session["interval_ms"],
        "start_time": session["start_time"].isoformat()
    }), 200


# =====================================================
# 8. TELEMETRY INGESTION
# =====================================================

@app.route("/telemetry", methods=["POST"])
def receive_telemetry():

    data = request.get_json(silent=True)

    if not isinstance(data, dict):
        return jsonify({"error": "Invalid JSON payload"}), 400

    required_fields = [
        "device_id",
        "zone_id",
        "temperature",
        "humidity",
        "accel_x",
        "accel_y",
        "accel_z",
        "water_raw",
        "load_raw",
        "load_kg",
        "quality_flag",
        "sequence_number",
        "device_timestamp_ms",
        "wifi_reconnect_count"
    ]

    missing_fields = [
        field for field in required_fields
        if field not in data
    ]

    if missing_fields:
        return jsonify({
            "error": "Missing required fields",
            "fields": missing_fields
        }), 400

    with lock:

        if not session["active"]:
            return jsonify({
                "error": "No active session"
            }), 403

        current_session_id = session["session_id"]

    payload_session_id = data.get("session_id")

    if payload_session_id != current_session_id:
        return jsonify({
            "error": "Session ID mismatch",
            "expected": current_session_id,
            "received": payload_session_id
        }), 409

    try:

        numeric_fields = [
            "temperature",
            "humidity",
            "accel_x",
            "accel_y",
            "accel_z",
            "water_raw",
            "load_raw",
            "load_kg",
            "sequence_number",
            "device_timestamp_ms",
            "wifi_reconnect_count"
        ]

        for field in numeric_fields:

            value = float(data[field])

            if not math.isfinite(value):
                raise ValueError(
                    f"Invalid numeric value: {field}"
                )

        received_at = datetime.now(timezone.utc)

        device_timestamp_ms = int(
            data["device_timestamp_ms"]
        )

        device_time = datetime.fromtimestamp(
            device_timestamp_ms / 1000,
            tz=timezone.utc
        )

        latency_ms = (
            received_at - device_time
        ).total_seconds() * 1000

        latency_valid = (
            0 <= latency_ms <= 60000
        )

        sequence_number = int(
            data["sequence_number"]
        )

        reconnect_count = int(
            data["wifi_reconnect_count"]
        )

        # -------------------------------
        # INFLUXDB POINT
        # -------------------------------

        point = (
            Point("tunnel_telemetry")
            .tag("device_id", str(data["device_id"]))
            .tag("gateway_id", str(data.get("gateway_id", "gateway01")))
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

            .field("sequence_number", sequence_number)
            .field("wifi_reconnect_count", reconnect_count)

            .field("latency_ms", float(latency_ms))
            .field("latency_valid", bool(latency_valid))

            .time(received_at, WritePrecision.NS)
        )

        # -------------------------------
        # WRITE TO INFLUXDB
        # -------------------------------

        write_api.write(
            bucket=INFLUXDB_BUCKET,
            org=INFLUXDB_ORG,
            record=point
        )

        # -------------------------------
        # FULL CONTINUOUS RECORD
        # -------------------------------

        full_record = dict(data)

        full_record.update({

            "session_id": current_session_id,

            "sequence_number": sequence_number,

            "received_at": received_at.isoformat(),

            "device_timestamp_ms": device_timestamp_ms,

            "latency_ms": round(latency_ms, 3),

            "latency_valid": latency_valid,

            "wifi_reconnect_count": reconnect_count

        })

        append_jsonl(
            CONTINUOUS_LOG_FILE,
            full_record
        )

        # -------------------------------
        # RELIABILITY RECORD
        # -------------------------------

        reliability_record = {

            "session_id": current_session_id,

            "sequence_number": sequence_number,

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

            "status": "success",

            "message": "Telemetry stored successfully",

            "session_id": current_session_id,

            "sequence_number": sequence_number,

            "latency_ms": round(latency_ms, 3),

            "latency_valid": latency_valid

        }), 200

    except Exception as error:

        app.logger.exception("Telemetry processing failed")

        return jsonify({
            "error": str(error)
        }), 500


# =====================================================
# 9. STOP SESSION
# =====================================================

@app.route("/session/stop", methods=["POST"])
def stop_session():

    with lock:

        if not session["active"]:
            return jsonify({
                "error": "No active session"
            }), 409

        session["active"] = False

        session["stop_time"] = datetime.now(
            timezone.utc
        )

    return jsonify({
        "message": "Session stopped",
        "session_id": session["session_id"],
        "stop_time": session["stop_time"].isoformat()
    }), 200


# =====================================================
# 10. RELIABILITY SUMMARY
# =====================================================

@app.route("/reliability/summary", methods=["GET"])
def reliability_summary():

    if not session["start_time"]:
        return jsonify({
            "error": "No session information available"
        }), 400

    end_time = (
        session["stop_time"]
        or datetime.now(timezone.utc)
    )

    duration_seconds = (
        end_time - session["start_time"]
    ).total_seconds()

    expected = (
        int(duration_seconds * 1000 / session["interval_ms"]) + 1
    )

    records = []

    if RELIABILITY_LOG_FILE.exists():

        with open(
            RELIABILITY_LOG_FILE,
            "r",
            encoding="utf-8"
        ) as file:

            for line in file:

                try:

                    record = json.loads(line)

                    if record.get("session_id") == session["session_id"]:
                        records.append(record)

                except json.JSONDecodeError:
                    continue

    unique_sequences = set(
        record["sequence_number"]
        for record in records
    )

    received = len(unique_sequences)

    missing = max(0, expected - received)

    latencies = [
        record["latency_ms"]
        for record in records
        if record.get("latency_valid")
    ]

    reconnect_counts = [
        record["wifi_reconnect_count"]
        for record in records
    ]

    reconnection_events = (
        max(reconnect_counts) - min(reconnect_counts)
        if reconnect_counts else 0
    )

    return jsonify({

        "session_id": session["session_id"],

        "duration_seconds": round(duration_seconds, 2),

        "expected_readings": expected,

        "received_readings": received,

        "missing_readings": missing,

        "duplicate_readings": len(records) - received,

        "average_latency_ms": (
            round(sum(latencies) / len(latencies), 3)
            if latencies else None
        ),

        "maximum_latency_ms": (
            round(max(latencies), 3)
            if latencies else None
        ),

        "reconnection_events": reconnection_events

    }), 200


# =====================================================
# 11. RUN SERVER
# =====================================================

if __name__ == "__main__":

    print("=" * 55)
    print("KARNAPHULI SHM HTTP INGESTION API")
    print("=" * 55)

    print("Project directory:", BASE_DIR)

    print("Continuous log:", CONTINUOUS_LOG_FILE)

    print("Reliability log:", RELIABILITY_LOG_FILE)

    print("InfluxDB:", INFLUXDB_URL)

    print("=" * 55)

    app.run(
        host="0.0.0.0",
        port=5000,
        threaded=True,
        debug=False
    )