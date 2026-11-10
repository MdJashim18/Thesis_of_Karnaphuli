import os
import json
import math
import threading

from pathlib import Path
from datetime import datetime, timezone

from flask import Flask, request, jsonify
from dotenv import load_dotenv

from influxdb_client import (
    InfluxDBClient,
    Point,
    WritePrecision
)

from influxdb_client.client.write_api import SYNCHRONOUS


# =====================================================
# 1. PATH CONFIGURATION
# =====================================================

BASE_DIR = Path(__file__).resolve().parent.parent

DATA_DIR = BASE_DIR / "data" / "raw"

DATA_DIR.mkdir(
    parents=True,
    exist_ok=True
)

CONTINUOUS_LOG_FILE = (
    DATA_DIR / "continuous_24h.jsonl"
)

RELIABILITY_LOG_FILE = (
    DATA_DIR / "reliability_log.jsonl"
)


# =====================================================
# 2. ENVIRONMENT CONFIGURATION
# =====================================================

load_dotenv(BASE_DIR / ".env")

INFLUXDB_URL = os.getenv(
    "INFLUXDB_URL",
    "http://localhost:8086"
)

INFLUXDB_TOKEN = os.getenv("INFLUXDB_TOKEN")

INFLUXDB_ORG = os.getenv(
    "INFLUXDB_ORG",
    "karnaphuli-lab"
)

INFLUXDB_BUCKET = os.getenv(
    "INFLUXDB_BUCKET",
    "tunnel_telemetry"
)


if not all([
    INFLUXDB_URL,
    INFLUXDB_TOKEN,
    INFLUXDB_ORG,
    INFLUXDB_BUCKET
]):

    raise RuntimeError(
        "InfluxDB configuration missing in .env"
    )


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

    with open(
        file_path,
        "a",
        encoding="utf-8"
    ) as file:

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

        "continuous_log": str(
            CONTINUOUS_LOG_FILE
        ),

        "reliability_log": str(
            RELIABILITY_LOG_FILE
        )

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

        try:

            interval_ms = int(
                data.get("interval_ms", 1000)
            )

        except (ValueError, TypeError):

            return jsonify({

                "error": "interval_ms must be an integer"

            }), 400

        if interval_ms <= 0:

            return jsonify({

                "error": "Invalid interval_ms"

            }), 400

        session_id = data.get(
            "session_id",
            "SHM-TEST-001"
        )

        if not isinstance(session_id, str) or not session_id.strip():

            return jsonify({

                "error": "Invalid session_id"

            }), 400

        session["active"] = True

        session["session_id"] = session_id

        session["start_time"] = datetime.now(
            timezone.utc
        )

        session["stop_time"] = None

        session["interval_ms"] = interval_ms

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

        return jsonify({

            "error": "Invalid JSON payload"

        }), 400

    # -------------------------------------------------
    # REQUIRED FIELDS
    # -------------------------------------------------

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
        "load_gram",
        "load_calibrated",
        "hx711_valid",

        "dht_valid",
        "mpu_valid",

        "quality_flag",

        "sequence_number",
        "device_timestamp_ms",
        "wifi_reconnect_count"

    ]

    missing_fields = [

        field

        for field in required_fields

        if field not in data

    ]

    if missing_fields:

        return jsonify({

            "error": "Missing required fields",

            "fields": missing_fields

        }), 400

    # -------------------------------------------------
    # SESSION VALIDATION
    # -------------------------------------------------

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

        # -------------------------------------------------
        # NUMERIC VALIDATION
        # -------------------------------------------------

        numeric_fields = [

            "temperature",
            "humidity",

            "accel_x",
            "accel_y",
            "accel_z",

            "water_raw",

            "load_raw",
            "load_kg",
            "load_gram",

            "sequence_number",
            "device_timestamp_ms",
            "wifi_reconnect_count"

        ]

        numeric_values = {}

        for field in numeric_fields:

            value = float(data[field])

            if not math.isfinite(value):

                raise ValueError(
                    f"Invalid numeric value: {field}"
                )

            numeric_values[field] = value

        # -------------------------------------------------
        # BOOLEAN VALIDATION
        # -------------------------------------------------

        boolean_fields = [

            "load_calibrated",
            "hx711_valid",

            "dht_valid",
            "mpu_valid"

        ]

        for field in boolean_fields:

            if not isinstance(data[field], bool):

                raise ValueError(
                    f"{field} must be a JSON boolean"
                )

        # -------------------------------------------------
        # STRING VALIDATION
        # -------------------------------------------------

        if not isinstance(data["quality_flag"], str):

            raise ValueError(
                "quality_flag must be a string"
            )

        # -------------------------------------------------
        # TIMESTAMP
        # -------------------------------------------------

        received_at = datetime.now(timezone.utc)

        device_timestamp_ms = int(
            numeric_values["device_timestamp_ms"]
        )

        if device_timestamp_ms > 0:

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

        else:

            latency_ms = None
            latency_valid = False

        # -------------------------------------------------
        # SEQUENCE AND RECONNECTION
        # -------------------------------------------------

        sequence_number = int(
            numeric_values["sequence_number"]
        )

        reconnect_count = int(
            numeric_values["wifi_reconnect_count"]
        )

        if sequence_number < 0 or reconnect_count < 0:

            raise ValueError(
                "Sequence and reconnection counts cannot be negative"
            )

        # =================================================
        # 9. MAIN TUNNEL TELEMETRY POINT
        # =================================================

        point = (

            Point("tunnel_telemetry")

            # ----- TAGS -----

            .tag(
                "device_id",
                str(data["device_id"])
            )

            .tag(
                "gateway_id",
                str(data.get("gateway_id", "gateway01"))
            )

            .tag(
                "zone_id",
                str(data["zone_id"])
            )

            .tag(
                "quality_flag",
                str(data["quality_flag"])
            )

            # ----- ENVIRONMENTAL SENSORS -----

            .field(
                "temperature",
                numeric_values["temperature"]
            )

            .field(
                "humidity",
                numeric_values["humidity"]
            )

            # ----- MPU6050 -----

            .field(
                "accel_x",
                numeric_values["accel_x"]
            )

            .field(
                "accel_y",
                numeric_values["accel_y"]
            )

            .field(
                "accel_z",
                numeric_values["accel_z"]
            )

            # ----- WATER SENSOR -----

            .field(
                "water_raw",
                int(numeric_values["water_raw"])
            )

            # ----- LOAD CELL -----

            .field(
                "load_raw",
                int(numeric_values["load_raw"])
            )

            .field(
                "load_kg",
                numeric_values["load_kg"]
            )

            .field(
                "load_gram",
                numeric_values["load_gram"]
            )

            .field(
                "load_calibrated",
                data["load_calibrated"]
            )

            .field(
                "hx711_valid",
                data["hx711_valid"]
            )

            # ----- SENSOR VALIDITY -----

            .field(
                "dht_valid",
                data["dht_valid"]
            )

            .field(
                "mpu_valid",
                data["mpu_valid"]
            )

            # ----- RELIABILITY -----

            .field(
                "sequence_number",
                sequence_number
            )

            .field(
                "wifi_reconnect_count",
                reconnect_count
            )

            .field(
                "latency_valid",
                bool(latency_valid)
            )

            .time(
                received_at,
                WritePrecision.NS
            )

        )

        if latency_ms is not None:

            point.field(
                "latency_ms",
                float(latency_ms)
            )

        # =================================================
        # 10. SEPARATE LOAD CELL POINT
        # =================================================

        load_point = (

            Point("load_cell_telemetry")

            .tag(
                "device_id",
                str(data["device_id"])
            )

            .tag(
                "gateway_id",
                str(data.get("gateway_id", "gateway01"))
            )

            .tag(
                "zone_id",
                str(data["zone_id"])
            )

            .tag(
                "status",
                (
                    "valid"
                    if (
                        data["hx711_valid"]
                        and data["load_calibrated"]
                    )
                    else "invalid"
                )
            )

            .field(
                "load_raw",
                int(numeric_values["load_raw"])
            )

            .field(
                "load_kg",
                numeric_values["load_kg"]
            )

            .field(
                "load_gram",
                numeric_values["load_gram"]
            )

            .field(
                "load_calibrated",
                data["load_calibrated"]
            )

            .field(
                "hx711_valid",
                data["hx711_valid"]
            )

            .time(
                received_at,
                WritePrecision.NS
            )

        )

        # =================================================
        # 11. WRITE TO INFLUXDB
        # =================================================

        write_api.write(

            bucket=INFLUXDB_BUCKET,

            org=INFLUXDB_ORG,

            record=[
                point,
                load_point
            ]

        )

        # =================================================
        # 12. FULL CONTINUOUS JSONL RECORD
        # =================================================

        full_record = dict(data)

        full_record.update({

            "session_id": current_session_id,

            "sequence_number": sequence_number,

            "received_at": received_at.isoformat(),

            "device_timestamp_ms": device_timestamp_ms,

            "latency_ms": (
                round(latency_ms, 3)
                if latency_ms is not None
                else None
            ),

            "latency_valid": latency_valid,

            "wifi_reconnect_count": reconnect_count

        })

        append_jsonl(

            CONTINUOUS_LOG_FILE,

            full_record

        )

        # =================================================
        # 13. RELIABILITY JSONL RECORD
        # =================================================

        reliability_record = {

            "session_id": current_session_id,

            "sequence_number": sequence_number,

            "received_at": received_at.isoformat(),

            "device_timestamp_ms": device_timestamp_ms,

            "latency_ms": (
                round(latency_ms, 3)
                if latency_ms is not None
                else None
            ),

            "latency_valid": latency_valid,

            "wifi_reconnect_count": reconnect_count

        }

        append_jsonl(

            RELIABILITY_LOG_FILE,

            reliability_record

        )

        # =================================================
        # 14. SUCCESS RESPONSE
        # =================================================

        return jsonify({

            "status": "success",

            "message": "Telemetry stored successfully",

            "session_id": current_session_id,

            "sequence_number": sequence_number,

            "load_raw": int(numeric_values["load_raw"]),

            "load_kg": numeric_values["load_kg"],

            "load_gram": numeric_values["load_gram"],

            "load_calibrated": data["load_calibrated"],

            "hx711_valid": data["hx711_valid"],

            "latency_ms": (
                round(latency_ms, 3)
                if latency_ms is not None
                else None
            ),

            "latency_valid": latency_valid,

            "influxdb_saved": True,

            "continuous_jsonl_saved": True,

            "reliability_jsonl_saved": True

        }), 200

    except Exception as error:

        app.logger.exception(
            "Telemetry processing failed"
        )

        return jsonify({

            "status": "error",

            "error": str(error)

        }), 500


# =====================================================
# 15. STOP SESSION
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
# 16. RELIABILITY SUMMARY
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

        int(
            duration_seconds * 1000 /
            session["interval_ms"]
        ) + 1

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

                    if (
                        record.get("session_id")
                        == session["session_id"]
                    ):

                        records.append(record)

                except json.JSONDecodeError:

                    continue

    # -------------------------------------------------
    # UNIQUE SEQUENCE NUMBERS
    # -------------------------------------------------

    unique_sequences = set(

        record["sequence_number"]

        for record in records

    )

    received = len(unique_sequences)

    missing = max(
        0,
        expected - received
    )

    # -------------------------------------------------
    # LATENCY
    # -------------------------------------------------

    latencies = [

        record["latency_ms"]

        for record in records

        if (
            record.get("latency_valid")
            and record.get("latency_ms") is not None
        )

    ]

    # -------------------------------------------------
    # WIFI RECONNECTION
    # -------------------------------------------------

    reconnect_counts = [

        record["wifi_reconnect_count"]

        for record in records

    ]

    reconnection_events = (

        max(reconnect_counts) - min(reconnect_counts)

        if reconnect_counts

        else 0

    )

    # -------------------------------------------------
    # RESPONSE
    # -------------------------------------------------

    return jsonify({

        "session_id": session["session_id"],

        "duration_seconds": round(
            duration_seconds,
            2
        ),

        "expected_readings": expected,

        "received_readings": received,

        "missing_readings": missing,

        "duplicate_readings": len(records) - received,

        "average_latency_ms": (

            round(
                sum(latencies) / len(latencies),
                3
            )

            if latencies

            else None

        ),

        "maximum_latency_ms": (

            round(
                max(latencies),
                3
            )

            if latencies

            else None

        ),

        "reconnection_events": reconnection_events

    }), 200


# =====================================================
# 17. RUN SERVER
# =====================================================

if __name__ == "__main__":

    print("=" * 55)

    print("KARNAPHULI SHM HTTP INGESTION API")

    print("=" * 55)

    print("Project directory:", BASE_DIR)

    print("Continuous log:", CONTINUOUS_LOG_FILE)

    print("Reliability log:", RELIABILITY_LOG_FILE)

    print("InfluxDB:", INFLUXDB_URL)

    print("InfluxDB Bucket:", INFLUXDB_BUCKET)

    print("=" * 55)

    app.run(

        host="0.0.0.0",

        port=5000,

        threaded=True,

        debug=False

    )