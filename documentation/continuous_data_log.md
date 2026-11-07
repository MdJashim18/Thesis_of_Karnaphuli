# Day 27: Continuous Data Collection Log

## 1. Experiment Overview

| Item | Details |
|---|---|
| Project | Karnaphuli Tunnel Structural Health Monitoring (SHM) Prototype |
| Experiment | Day 27 – Continuous Data Collection |
| Session ID | SHM-TEST-001 |
| Device ID | ESP32-GW-LAB-001 |
| Gateway ID | gateway01 |
| Zone ID | LAB_PROTOTYPE |
| Backend | Flask HTTP Ingestion API |
| Database | InfluxDB OSS 2.9.1 |
| Data Storage | JSONL and InfluxDB |

## 2. Data Collection Period

- Start Time (UTC): 2026-11-03 05:38:16.496835
- End Time (UTC): 2026-11-06 13:29:30.072617
- Start Time (Bangladesh): 2026-11-03 11:38:16.496835
- End Time (Bangladesh): 2026-11-06 19:29:30.072617
- Total Duration: 287,473.58 seconds
- Approximate Duration: 79 hours 51 minutes 13 seconds

## 3. Data Collection Summary

| Metric | Value |
|---|---:|
| Expected Readings | 287,474 |
| Received Readings | 1,243 |
| Estimated Missing Readings | 286,231 |
| Estimated Missing Rate | 99.57% |
| Valid Latency Samples | 639 |
| Average Latency | 3,614.34 ms |
| Reconnection Counter Increments | 41 |

**Important Note:** Expected readings were calculated using an assumed one-second sampling interval. Therefore, the estimated missing readings and missing rate do not represent confirmed packet loss. The actual firmware sampling and transmission intervals must be verified before drawing a definitive conclusion.

## 4. Data File Analysis

Two JSONL files were analyzed:

- data/raw/continuous_24h.jsonl
- data/raw/reliability_log.jsonl

| File | Total Records |
|---|---:|
| continuous_24h.jsonl | 1,243 |
| reliability_log.jsonl | 1,243 |

Both files contained records from session SHM-TEST-001.

### 4.1 Data Quality Distribution

| Quality Status | Records |
|---|---:|
| Partial | 1,241 |
| Degraded | 2 |
| Total | 1,243 |

Most records were classified as partial, indicating that the current data-quality validation or sensor telemetry requires further investigation.

### 4.2 Sensor Data Validation

| Sensor / Parameter | Observation |
|---|---|
| DHT22 | Valid in all 1,243 records |
| MPU6050 | Valid in all 1,243 records |
| HX711 | Valid in 1,241 records |
| Water Sensor | water_raw = 0 in 1,200 records |
| Load Cell | load_kg = 0.0 in all records |

Although DHT22 and MPU6050 validity flags were true, further physical validation is necessary to confirm measurement accuracy.

The load-cell output requires investigation because the converted load_kg value remained zero in all records despite variations in raw readings.

The water sensor also requires additional calibration and testing because most recorded values were zero.

## 5. Network Latency Analysis

| Metric | Result |
|---|---:|
| Valid Latency Samples | 639 |
| Invalid Latency Samples | 604 |
| Average Latency | 3,614.34 ms |
| Minimum Valid Latency | 0.299 ms |
| Maximum Valid Latency | 52,087.701 ms |

The average latency was calculated using only valid latency samples.

Some device timestamps were zero or invalid. Therefore, NTP synchronization and timestamp validation should be improved before conducting further network-performance analysis.

## 6. Wi-Fi Reconnection Analysis

The analysis script reported 41 reconnection counter increments.

Additional log inspection revealed:

- Maximum observed reconnect counter: 17
- Counter reset or decreased 5 times.
- The value 41 represents the sum of positive counter increments, not necessarily 41 individually timestamped reconnection events.

For more accurate reliability analysis, each Wi-Fi disconnection and successful reconnection should be recorded as a separate event with a timestamp.

## 7. Sequence Number Analysis

| Sequence Number | Records |
|---|---:|
| 0 | 1,235 |
| 137 | 8 |

The sequence number was not incrementing correctly for every reading.

This prevents reliable identification of missing, duplicate, or out-of-order telemetry records.

A continuously increasing sequence number should be implemented in the ESP32 firmware.

## 8. InfluxDB Storage Verification

The JSONL files confirm that telemetry records were written to local storage.

However, the JSONL files alone cannot confirm that all records were successfully stored in InfluxDB.

InfluxDB storage should be independently verified using the Data Explorer or Flux queries.

**InfluxDB Configuration:**

- Organization: karnaphuli-lab
- Bucket: tunnel_telemetry
- Database Version: InfluxDB OSS 2.9.1

The total number of stored records should be compared with the number of records received by the Flask API.

## 9. Identified Problems

1. The sequence number was not incrementing correctly.
2. Most telemetry records were classified as partial.
3. Several device timestamps were invalid.
4. The average latency was relatively high.
5. The Wi-Fi reconnect counter reset multiple times.
6. The load-cell converted value remained zero.
7. The water sensor frequently returned zero.
8. The actual sampling interval needs verification.
9. InfluxDB persistence requires independent verification.

## 10. Recommended Improvements

### 10.1 Firmware Improvements

- Implement a continuously increasing sequence number.
- Verify the sampling and transmission intervals.
- Improve Wi-Fi reconnection handling.
- Add individual reconnection-event logging.
- Improve NTP synchronization.
- Validate device timestamps before calculating latency.

### 10.2 Sensor Improvements

- Recheck HX711 calibration and load conversion.
- Verify the load-cell values in the HTTP payload.
- Recheck water sensor wiring and ADC readings.
- Perform additional sensor calibration tests.
- Validate sensor measurements against known reference values.

### 10.3 Backend Improvements

- Improve telemetry quality classification.
- Log HTTP transmission failures.
- Record server-side timestamps consistently.
- Verify InfluxDB data persistence.
- Compare local JSONL records with database records.

## 11. Next Steps: Controlled 24-Hour Data Collection

1. Fix the sequence-number mechanism.
2. Verify the actual sampling interval.
3. Confirm successful NTP synchronization.
4. Validate all sensor readings.
5. Confirm HTTP responses from the Flask API.
6. Verify data storage in InfluxDB.
7. Start a new session with a unique session ID.
8. Record the experiment start time.
9. Run the prototype continuously for 24 hours.
10. Calculate missing readings using verified sequence numbers.
11. Calculate average latency using valid timestamps.
12. Count reconnection events using individual event logs.
13. Preserve all raw data and analysis results.

## 12. Conclusion

The Day 27 experiment demonstrated that the ESP32-based Structural Health Monitoring prototype could generate and record telemetry data over an extended period.

The system successfully produced 1,243 records across approximately 79 hours and 51 minutes. However, several reliability and data-quality issues were identified, particularly in sequence numbering, timestamp synchronization, sensor-value conversion, and Wi-Fi reconnection logging.

The estimated 99.57% missing rate is based on an assumed one-second sampling interval and should not be interpreted as confirmed packet loss.

Therefore, this experiment should be considered an **initial long-duration operational test**, rather than a verified uninterrupted 24-hour data collection experiment.

After correcting the identified issues, a controlled 24-hour data collection experiment should be conducted to obtain more reliable performance and reliability measurements for the Karnaphuli Tunnel Structural Health Monitoring prototype.