# Month 2 Final Dataset and System Report

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
| Valid JSON records | 3483 |
| CSV data rows | 3483 |
| JSON parsing errors | 0 |
| CSV columns | 30 |
| Exact duplicate JSON records | 0 |
| Collection start | 2026-11-03 05:38:16.496835+00:00 |
| Collection end | 2026-11-09 17:35:42.278546+00:00 |
| Collection duration (hours) | 155.96 |

Note: The filename `continuous_24h.jsonl` does not establish
that the dataset covers exactly 24 hours. The observed duration
is calculated from the received_at timestamps.

## 4. Data Quality Distribution

| Quality flag | Records |
| degraded | 3 |
| ok | 1068 |
| partial | 2412 |

## 5. Load Cell Calibration Status

| Calibration state | Records |
|---|---:|
| True | 1068 |
| False | 959 |
| Missing or null | 1456 |

### Quality by calibration state

| Quality | Calibration state | Records |
|---|---|---:|
| degraded | MISSING | 2 |\n| degraded | False | 1 |\n| ok | True | 1068 |\n| partial | MISSING | 1454 |\n| partial | False | 958 |\n
The observed dataset shows that all records marked `ok`
have `load_calibrated=True`. This is an observed association;
the firmware quality-classification logic should be reviewed
before attributing causality exclusively to calibration.

## 6. Timestamp and Latency Validation

| Metric | Result |
|---|---:|
| Total zero/invalid device timestamps | 87 |
| Original latency_valid=true records | 1729 |
| Audit-valid latency records | 1729 |
| Original valid-flag mean latency (ms) | 2890.32 |
| Audit-valid mean latency (ms) | 2890.32 |

Records with zero device timestamps are retained in the CSV.
Their timestamp validity is marked false. Latency values are
not considered audit-valid when the device timestamp is invalid
or the latency is negative.

## 7. Boot ID and Sequence Analysis

| Metric | Result |
|---|---:|
| Records with boot_id | 285 |
| Records missing boot_id | 3198 |
| Adjacent sequence decreases | 53 |

Sequence decreases do not independently prove ESP32 reboots.
Because many records lack boot_id, sequence resets and possible
interleaving cannot be conclusively distinguished.

Exact duplicate JSON records were checked separately. Sequence
key collisions must not automatically be treated as duplicate
telemetry records.

## 8. Degraded Records

Total degraded records: 3.

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

1. The collection duration is approximately 155.96
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
