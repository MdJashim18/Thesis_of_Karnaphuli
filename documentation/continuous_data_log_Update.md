# Day 28: Continuous Data Collection Monitoring Log

## 1. Objective

The primary objective of Day 28 was to continue the ongoing sensor data collection process and monitor the operational status of the ESP32 device, Python HTTP API, and InfluxDB database.

The main focus was to ensure continuous data transmission, successful database storage, and proper operation of the overall data collection system.

## 2. System Configuration

The existing Karnaphuli Tunnel Structural Health Monitoring (SHM) prototype configuration was maintained.

| Component | Configuration |
|---|---|
| Microcontroller | ESP32 DOIT DEVKIT V1 |
| Sensor Communication | Wi-Fi |
| Data Transmission | HTTP POST |
| Backend Server | Python Flask |
| API Port | 5000 |
| Database | InfluxDB OSS 2.9.1 |
| Organization | karnaphuli-lab |
| Bucket | tunnel_telemetry |
| Raw Data Logging | JSONL |
| Device ID | ESP32-GW-LAB-001 |
| Gateway ID | gateway01 |
| Zone ID | LAB_PROTOTYPE |

## 3. System Operational Status

All major components were checked during Day 28 monitoring.

| Component | Status | Observation |
|---|---|---|
| ESP32 Device | Operational | Working correctly |
| Wi-Fi Connection | Operational | Connection verified |
| Python HTTP API | Operational | Server running properly |
| Flask Server | Operational | No blocking issue observed |
| HTTP Communication | Operational | Data transmission verified |
| InfluxDB | Operational | Database accessible |
| JSONL Data Logging | Operational | Data logging verified |

## 4. Monitoring Activities

The following monitoring activities were completed:

1. Checked whether the ESP32 device remained connected to Wi-Fi.
2. Verified that the Python HTTP API was running.
3. Monitored HTTP communication between ESP32 and the backend server.
4. Checked whether incoming telemetry data was being processed.
5. Verified that new sensor data was arriving in InfluxDB.
6. Checked the JSONL files for newly appended records.
7. Reviewed recent sensor readings and timestamps.
8. Monitored the system for Python, HTTP, and database-related errors.

## 5. Data Collection Monitoring

The following data collection files were monitored:

- `data/raw/continuous_24h.jsonl`
- `data/raw/reliability_log.jsonl`

Both files were checked to verify that the data logging process was functioning correctly.

The latest records were inspected to confirm that new telemetry information was being appended.

## 6. InfluxDB Verification

The InfluxDB database was accessed through its web interface.

The following checks were performed:

- Verified access to the InfluxDB dashboard.
- Checked the `tunnel_telemetry` bucket.
- Inspected recent telemetry records using Data Explorer.
- Verified that new data was available in the database.
- Checked the timestamps of recent records.

The database monitoring process was completed successfully.

## 7. Error and Reliability Monitoring

During the Day 28 monitoring activities, the following areas were checked:

| Error Category | Monitoring Result |
|---|---|
| Python API Errors | No issue observed |
| InfluxDB Connection | Working correctly |
| HTTP Communication | Working correctly |
| Wi-Fi Connection | Working correctly |
| JSONL File Logging | Working correctly |
| Database Accessibility | Verified |
| General System Operation | Normal |

No critical operational issue was observed during the monitoring activities.

## 8. Sensor Data Monitoring

The sensor data transmission process was checked through the ESP32 and backend monitoring environment.

The following sensor categories were included:

- Temperature and humidity (DHT22)
- Vibration and acceleration (MPU6050)
- Water level (HW-038)
- Load measurement (HX711)

The overall sensor data monitoring process was completed.

## 9. Issues Identified

No new critical system-level issue was identified during Day 28 monitoring.

The existing system configuration was maintained without introducing unnecessary changes to the firmware, API, or database configuration.

Previously identified data quality and sensor calibration issues remain subjects for further investigation and validation.

## 10. Conclusion

Day 28 focused on maintaining and monitoring the continuous data collection infrastructure developed for the Karnaphuli Tunnel Structural Health Monitoring prototype.

The ESP32 device, Wi-Fi communication, Python HTTP API, and InfluxDB database were checked successfully. The JSONL logging process was also verified to ensure that incoming telemetry data was being recorded.

All planned monitoring activities were completed, and the system was found to be operational during the checks.

No critical operational interruption was identified during the monitoring process.

## 11. Next Steps

The following activities will be continued in the next phase:

1. Maintain continuous sensor data collection.
2. Continue monitoring Python API and InfluxDB operations.
3. Monitor network reliability and communication errors.
4. Investigate previously identified sensor data quality issues.
5. Verify data completeness and timestamp consistency.
6. Continue updating the continuous data collection documentation.