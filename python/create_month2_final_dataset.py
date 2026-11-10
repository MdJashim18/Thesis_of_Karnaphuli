
import json
import csv
from pathlib import Path
from collections import Counter
from datetime import datetime

PROJECT = Path(r"D:\karnaphuli-shm-month2")

INPUT_FILE = PROJECT / "data" / "raw" / "continuous_24h.jsonl"
OUTPUT_FILE = PROJECT / "data" / "raw" / "month2_final_dataset.csv"
REPORT_FILE = PROJECT / "documentation" / "month2_final_report.md"

OUTPUT_FILE.parent.mkdir(parents=True, exist_ok=True)
REPORT_FILE.parent.mkdir(parents=True, exist_ok=True)

# --------------------------------------------------
# 1. READ JSONL
# --------------------------------------------------

records = []
json_errors = []

with open(INPUT_FILE, "r", encoding="utf-8") as f:
    for line_number, line in enumerate(f, start=1):
        if not line.strip():
            continue

        try:
            records.append(json.loads(line))
        except json.JSONDecodeError as e:
            json_errors.append((line_number, str(e)))

if not records:
    raise RuntimeError("No valid records found in JSONL.")

# Preserve all original fields across all records.
original_fields = sorted({
    key
    for record in records
    for key in record.keys()
})

audit_fields = [
    "record_index",
    "device_timestamp_valid",
    "boot_id_status",
    "load_calibration_status",
    "latency_audit_valid"
]

fieldnames = original_fields + audit_fields

# --------------------------------------------------
# 2. ADD AUDIT FIELDS WITHOUT DELETING DATA
# --------------------------------------------------

csv_rows = []

for index, record in enumerate(records, start=1):
    row = dict(record)

    timestamp = record.get("device_timestamp_ms")
    try:
        timestamp_valid = (
            timestamp is not None and float(timestamp) > 0
        )
    except (ValueError, TypeError):
        timestamp_valid = False

    boot_id = record.get("boot_id")
    boot_status = (
        "present"
        if boot_id is not None and str(boot_id).strip()
        else "missing"
    )

    calibration = record.get("load_calibrated")

    if calibration is True:
        calibration_status = "calibrated"
    elif calibration is False:
        calibration_status = "not_calibrated"
    else:
        calibration_status = "missing"

    latency = record.get("latency_ms")
    original_latency_valid = record.get("latency_valid") is True

    try:
        latency_nonnegative = (
            latency is not None and float(latency) >= 0
        )
    except (ValueError, TypeError):
        latency_nonnegative = False

    latency_audit_valid = (
        original_latency_valid
        and timestamp_valid
        and latency_nonnegative
    )

    row.update({
        "record_index": index,
        "device_timestamp_valid": timestamp_valid,
        "boot_id_status": boot_status,
        "load_calibration_status": calibration_status,
        "latency_audit_valid": latency_audit_valid
    })

    csv_rows.append(row)

# --------------------------------------------------
# 3. WRITE CSV
# --------------------------------------------------

with open(OUTPUT_FILE, "w", newline="", encoding="utf-8-sig") as f:
    writer = csv.DictWriter(
        f,
        fieldnames=fieldnames,
        extrasaction="ignore"
    )
    writer.writeheader()
    writer.writerows(csv_rows)

# --------------------------------------------------
# 4. CALCULATE REPORT STATISTICS
# --------------------------------------------------

total = len(records)

quality_counts = Counter(
    r.get("quality_flag", "MISSING")
    for r in records
)

calibration_counts = Counter(
    (
        r.get("quality_flag", "MISSING"),
        r.get("load_calibrated", "MISSING")
    )
    for r in records
)

boot_counts = Counter(
    "present"
    if r.get("boot_id") is not None
    and str(r.get("boot_id")).strip()
    else "missing"
    for r in records
)

timestamp_invalid = sum(
    not row["device_timestamp_valid"]
    for row in csv_rows
)

latency_original_valid = [
    float(r["latency_ms"])
    for r in records
    if r.get("latency_valid") is True
    and isinstance(r.get("latency_ms"), (int, float))
]

latency_audit_valid = [
    float(r["latency_ms"])
    for r in csv_rows
    if r["latency_audit_valid"]
]

calibrated_count = sum(
    r.get("load_calibrated") is True
    for r in records
)

uncalibrated_count = sum(
    r.get("load_calibrated") is False
    for r in records
)

calibration_missing = sum(
    "load_calibrated" not in r
    or r.get("load_calibrated") is None
    for r in records
)

boot_missing = boot_counts["missing"]

sequence_decreases = 0

for previous, current in zip(records, records[1:]):
    p = previous.get("sequence_number")
    c = current.get("sequence_number")

    if (
        isinstance(p, int)
        and isinstance(c, int)
        and c < p
    ):
        sequence_decreases += 1

# Exact duplicate JSON records
canonical_records = [
    json.dumps(r, sort_keys=True, ensure_ascii=False)
    for r in records
]

exact_duplicate_count = (
    len(canonical_records) - len(set(canonical_records))
)

# Received-at duration
received_times = []

for r in records:
    value = r.get("received_at")
    if value:
        try:
            received_times.append(
                datetime.fromisoformat(value.replace("Z", "+00:00"))
            )
        except ValueError:
            pass

received_times.sort()

if len(received_times) >= 2:
    start_time = received_times[0]
    end_time = received_times[-1]
    duration_hours = (
        end_time - start_time
    ).total_seconds() / 3600
else:
    start_time = None
    end_time = None
    duration_hours = 0

average_latency = (
    sum(latency_original_valid) / len(latency_original_valid)
    if latency_original_valid else None
)

average_audit_latency = (
    sum(latency_audit_valid) / len(latency_audit_valid)
    if latency_audit_valid else None
)

# --------------------------------------------------
# 5. VALIDATE CSV ROW COUNT
# --------------------------------------------------

with open(OUTPUT_FILE, "r", encoding="utf-8-sig", newline="") as f:
    csv_record_count = sum(1 for _ in csv.DictReader(f))

if csv_record_count != total:
    raise RuntimeError(
        f"CSV row mismatch: JSONL={total}, CSV={csv_record_count}"
    )

# --------------------------------------------------
# 6. GENERATE FINAL REPORT
# --------------------------------------------------

def fmt(value):
    return "N/A" if value is None else f"{value:.2f}"

report = f"""# Month 2 Final Dataset and System Report

## 1. Project Overview

This report documents the Month 2 data collection and validation
for the Karnaphuli Tunnel Structural Health Monitoring (SHM)
laboratory prototype.

The dataset represents laboratory prototype measurements.
It must not be interpreted as actual structural measurements
from the operational Karnaphuli Tunnel.

## 2. Data Collection Architecture

Sensors → ESP32 → HTTP POST → Python Flask API
(http_ingest_api.py) → InfluxDB + JSONL

The primary dataset was collected from:

`data/raw/continuous_24h.jsonl`

The Flask API endpoint used in the project is `/telemetry`.

## 3. Dataset Summary

| Metric | Result |
|---|---:|
| Valid JSON records | {total} |
| CSV data rows | {csv_record_count} |
| JSON parsing errors | {len(json_errors)} |
| CSV columns | {len(fieldnames)} |
| Exact duplicate JSON records | {exact_duplicate_count} |
| Collection start | {start_time} |
| Collection end | {end_time} |
| Collection duration (hours) | {duration_hours:.2f} |

Note: The filename `continuous_24h.jsonl` does not establish
that the dataset covers exactly 24 hours. The observed duration
is calculated from the received_at timestamps.

## 4. Data Quality Distribution

| Quality flag | Records |
"""

for quality, count in sorted(quality_counts.items()):
    report += f"| {quality} | {count} |\n"

report += f"""
## 5. Load Cell Calibration Status

| Calibration state | Records |
|---|---:|
| True | {calibrated_count} |
| False | {uncalibrated_count} |
| Missing or null | {calibration_missing} |

### Quality by calibration state

| Quality | Calibration state | Records |
|---|---|---:|
"""

for (quality, calibration), count in sorted(
    calibration_counts.items(),
    key=lambda x: str(x[0])
):
    report += (
        f"| {quality} | {calibration} | {count} |\\n"
    )

report += f"""
The observed dataset shows that all records marked `ok`
have `load_calibrated=True`. This is an observed association;
the firmware quality-classification logic should be reviewed
before attributing causality exclusively to calibration.

## 6. Timestamp and Latency Validation

| Metric | Result |
|---|---:|
| Total zero/invalid device timestamps | {timestamp_invalid} |
| Original latency_valid=true records | {len(latency_original_valid)} |
| Audit-valid latency records | {len(latency_audit_valid)} |
| Original valid-flag mean latency (ms) | {fmt(average_latency)} |
| Audit-valid mean latency (ms) | {fmt(average_audit_latency)} |

Records with zero device timestamps are retained in the CSV.
Their timestamp validity is marked false. Latency values are
not considered audit-valid when the device timestamp is invalid
or the latency is negative.

## 7. Boot ID and Sequence Analysis

| Metric | Result |
|---|---:|
| Records with boot_id | {boot_counts["present"]} |
| Records missing boot_id | {boot_missing} |
| Adjacent sequence decreases | {sequence_decreases} |

Sequence decreases do not independently prove ESP32 reboots.
Because many records lack boot_id, sequence resets and possible
interleaving cannot be conclusively distinguished.

Exact duplicate JSON records were checked separately. Sequence
key collisions must not automatically be treated as duplicate
telemetry records.

## 8. Degraded Records

Total degraded records: {quality_counts.get("degraded", 0)}.

The inspected degraded records had `hx711_valid=False`.
These records are retained rather than silently discarded.

## 9. Dataset Preservation and Audit Fields

The final CSV preserves all original JSONL fields and records.
The following audit fields were added:

- `record_index`
- `device_timestamp_valid`
- `boot_id_status`
- `load_calibration_status`
- `latency_audit_valid`

No record was removed based on quality flag, sequence number,
calibration status, or timestamp validity.

## 10. Limitations

1. The collection duration is approximately {duration_hours:.2f}
   hours, not necessarily 24 hours.
2. Some device timestamps are zero.
3. Many records do not contain boot_id.
4. Sequence numbers are not consistently monotonic.
5. Load-cell calibration status is missing or false in many records.
6. Invalid and negative latency values exist.
7. The dataset represents a laboratory prototype, not live
   operational tunnel monitoring.
8. JSONL and InfluxDB record counts have not been independently
   reconciled in this report.

## 11. Output Files

- `data/raw/month2_final_dataset.csv`
- `documentation/month2_final_report.md`

## 12. Conclusion

The Month 2 JSONL dataset was parsed and exported to CSV with
record preservation and additional audit fields. Data quality
limitations are documented so that subsequent statistical
analysis and model development can distinguish valid,
uncalibrated, degraded, and timestamp-invalid observations.
"""

with open(REPORT_FILE, "w", encoding="utf-8") as f:
    f.write(report)

# --------------------------------------------------
# 7. FINAL CONSOLE SUMMARY
# --------------------------------------------------

print("=" * 65)
print("MONTH 2 FINAL DATASET EXPORT")
print("=" * 65)

print("JSONL records:", total)
print("CSV records:", csv_record_count)
print("CSV columns:", len(fieldnames))
print("JSON parsing errors:", len(json_errors))
print("Exact duplicate JSON records:", exact_duplicate_count)
print("Collection duration (hours):", round(duration_hours, 2))
print("Zero/invalid device timestamps:", timestamp_invalid)
print("Records with boot_id:", boot_counts["present"])
print("Records missing boot_id:", boot_missing)
print("Sequence decreases:", sequence_decreases)
print("Audit-valid latency records:", len(latency_audit_valid))

print("\nQuality distribution:")
for quality, count in sorted(quality_counts.items()):
    print(f"  {quality}: {count}")

print("\nCSV:", OUTPUT_FILE)
print("Report:", REPORT_FILE)

print("\nDataset export and validation completed successfully.")
