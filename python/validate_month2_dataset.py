
import json
import statistics
from pathlib import Path
from collections import Counter
from datetime import datetime, timezone

# ==========================================
# MONTH 2 DATASET VALIDATION
# ==========================================

PROJECT_DIR = Path(r"D:\karnaphuli-shm-month2")

INPUT_FILE = (
    PROJECT_DIR / "data" / "raw" / "continuous_24h.jsonl"
)

print("=" * 65)
print("KARNAPHULI SHM - MONTH 2 DATASET VALIDATION")
print("=" * 65)

records = []
parse_errors = []

# ------------------------------------------
# 1. Read JSONL
# ------------------------------------------

with open(INPUT_FILE, "r", encoding="utf-8") as f:
    for line_number, line in enumerate(f, start=1):
        line = line.strip()

        if not line:
            continue

        try:
            records.append(json.loads(line))
        except json.JSONDecodeError as e:
            parse_errors.append((line_number, str(e)))

print("\n[1] FILE INFORMATION")
print("File:", INPUT_FILE)
print("Total valid JSON records:", len(records))
print("JSON parsing errors:", len(parse_errors))

if not records:
    raise SystemExit("No valid records found.")

# ------------------------------------------
# 2. Timestamp analysis
# ------------------------------------------

received_times = []

for record in records:
    timestamp = record.get("received_at")

    if timestamp:
        try:
            dt = datetime.fromisoformat(
                timestamp.replace("Z", "+00:00")
            )

            if dt.tzinfo is None:
                dt = dt.replace(tzinfo=timezone.utc)

            received_times.append(dt)

        except (ValueError, TypeError):
            pass

print("\n[2] COLLECTION DURATION")

if received_times:
    first_time = min(received_times)
    last_time = max(received_times)

    duration = last_time - first_time

    print("First received_at:", first_time.isoformat())
    print("Last received_at:", last_time.isoformat())
    print("Duration:", duration)
    print("Duration in hours:", round(
        duration.total_seconds() / 3600, 2
    ))
else:
    print("No valid received_at timestamps.")

# ------------------------------------------
# 3. Device timestamp analysis
# ------------------------------------------

device_times = []

for record in records:
    value = record.get("device_timestamp_ms")

    try:
        if value is not None:
            device_times.append(
                datetime.fromtimestamp(
                    float(value) / 1000,
                    tz=timezone.utc
                )
            )
    except (ValueError, TypeError, OverflowError):
        pass

print("\n[3] DEVICE TIMESTAMP")
print("Valid device timestamps:", len(device_times))

if device_times:
    print("First device timestamp:", min(device_times))
    print("Last device timestamp:", max(device_times))

# ------------------------------------------
# 4. Quality distribution
# ------------------------------------------

quality_counts = Counter(
    str(r.get("quality_flag", "MISSING"))
    for r in records
)

print("\n[4] QUALITY FLAG DISTRIBUTION")

for quality, count in quality_counts.items():
    percentage = count / len(records) * 100
    print(
        f"{quality}: {count} "
        f"({percentage:.2f}%)"
    )

# ------------------------------------------
# 5. Sensor validity
# ------------------------------------------

print("\n[5] SENSOR VALIDITY")

for field in [
    "dht_valid",
    "mpu_valid",
    "hx711_valid",
    "load_calibrated"
]:
    present = sum(field in r for r in records)

    true_count = sum(
        r.get(field) is True for r in records
    )

    false_count = sum(
        r.get(field) is False for r in records
    )

    print(
        f"{field}: present={present}, "
        f"true={true_count}, false={false_count}, "
        f"missing={len(records)-present}"
    )

# ------------------------------------------
# 6. Field completeness
# ------------------------------------------

all_fields = sorted(
    set().union(*(r.keys() for r in records))
)

print("\n[6] FIELD COMPLETENESS")

for field in all_fields:
    present = sum(field in r for r in records)
    missing = len(records) - present

    print(
        f"{field}: present={present}, missing={missing}"
    )

# ------------------------------------------
# 7. Latency statistics
# ------------------------------------------

latencies = []

for r in records:
    value = r.get("latency_ms")

    if (
        r.get("latency_valid") is True
        and isinstance(value, (int, float))
    ):
        latencies.append(float(value))

print("\n[7] LATENCY ANALYSIS")

print("Valid latency records:", len(latencies))

if latencies:
    print("Average latency (ms):", round(
        statistics.mean(latencies), 2
    ))
    print("Minimum latency (ms):", round(
        min(latencies), 2
    ))
    print("Maximum latency (ms):", round(
        max(latencies), 2
    ))

    if len(latencies) > 1:
        print("Latency SD (ms):", round(
            statistics.stdev(latencies), 2
        ))

# ------------------------------------------
# 8. Sequence analysis
# ------------------------------------------

sequences = [
    r.get("sequence_number")
    for r in records
    if isinstance(r.get("sequence_number"), int)
]

print("\n[8] SEQUENCE ANALYSIS")
print("Records with sequence number:", len(sequences))
print("Unique sequence values:", len(set(sequences)))

if sequences:
    print("Minimum sequence:", min(sequences))
    print("Maximum sequence:", max(sequences))

# Duplicate key check
keys = [
    (
        r.get("device_id"),
        r.get("session_id"),
        r.get("sequence_number")
    )
    for r in records
    if r.get("sequence_number") is not None
]

duplicate_keys = len(keys) - len(set(keys))

print("Duplicate device/session/sequence keys:",
      duplicate_keys)

# ------------------------------------------
# 9. Missing and invalid values
# ------------------------------------------

print("\n[9] IMPORTANT FIELD CHECK")

important_fields = [
    "temperature",
    "humidity",
    "accel_x",
    "accel_y",
    "accel_z",
    "water_raw",
    "load_raw",
    "load_kg",
    "received_at",
    "device_timestamp_ms",
    "quality_flag"
]

for field in important_fields:
    missing = sum(
        field not in r or r[field] is None
        for r in records
    )

    print(f"{field}: missing/null={missing}")

# ------------------------------------------
# 10. Reconnection analysis
# ------------------------------------------

reconnect_values = [
    r.get("wifi_reconnect_count")
    for r in records
    if isinstance(r.get("wifi_reconnect_count"), int)
]

print("\n[10] WIFI RECONNECTION")

print("Records with reconnect counter:",
      len(reconnect_values))

if reconnect_values:
    print("First counter:", reconnect_values[0])
    print("Last counter:", reconnect_values[-1])
    print("Maximum counter:", max(reconnect_values))

    increases = sum(
        reconnect_values[i] > reconnect_values[i-1]
        for i in range(1, len(reconnect_values))
    )

    print("Observed counter increases:", increases)

# ------------------------------------------
# 11. Final summary
# ------------------------------------------

print("\n" + "=" * 65)
print("VALIDATION SUMMARY")
print("=" * 65)

print("Total records:", len(records))
print("JSON errors:", len(parse_errors))
print("Quality distribution:", dict(quality_counts))
print("Duplicate sequence keys:", duplicate_keys)

if received_times:
    print("Actual collection duration:", last_time - first_time)

print("\nValidation completed.")
