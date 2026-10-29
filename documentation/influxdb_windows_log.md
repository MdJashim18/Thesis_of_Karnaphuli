# Day 18: InfluxDB Windows Setup Log

## Objective
Configure InfluxDB for the Karnaphuli Tunnel Structural Health Monitoring (SHM) project and verify database connectivity through Python write/read operations.

## Software and Environment
- InfluxDB OSS: 2.9.1
- Operating System: Windows
- Python: 3.13.5
- pip: 26.2.1
- Python client library: `influxdb-client` 1.50.0
- Environment variable loader: `python-dotenv`
- Installation directory: `D:\Software\influxdb2-2.9.1-windows_amd64`

## Database Storage
- Database directory: `D:\karnaphuli-shm-month2\database`
- Engine data: `database\engine\data`
- Metadata file: `database\influxd.bolt`
- SQLite metadata: `database\influxd.sqlite`
- Storage location: D: drive

## InfluxDB Configuration
- Server URL: `http://localhost:8086`
- Organization: `karnaphuli-lab`
- Bucket: `tunnel_telemetry`
- Bucket retention: 365 days (configured; verify in bucket settings)
- Custom API token: Created and stored in `.env`
- Configuration file: `D:\karnaphuli-shm-month2\.env`

### Environment Variables
The `.env` file contains the following configuration keys:

- `INFLUXDB_URL`
- `INFLUXDB_ORG`
- `INFLUXDB_BUCKET`
- `INFLUXDB_TOKEN`

Actual credentials and token values are intentionally excluded from this log.

## Python Test Script
- Script: `test_influxdb.py`
- Project directory: `D:\karnaphuli-shm-month2`
- Purpose: Test InfluxDB connection, write a test point, and query the stored point.

## Python Write/Read Test

### Test Measurement
- Measurement: `influxdb_connection_test`
- Bucket: `tunnel_telemetry`
- Device tag: `ESP32-GW-LAB-001`
- Zone tag: `LAB_PROTOTYPE`
- Test tag: `true`

### Test Data
- Temperature: 28.4 (synthetic test value)
- Humidity: 72.1 (synthetic test value)

These are synthetic values used only to verify database connectivity. They are not actual ESP32 sensor readings.

### Test Results
- Python environment: PASS
- Environment configuration loaded: PASS
- InfluxDB connection: PASS
- Database write operation: PASS
- Database read/query operation: PASS
- Test measurement retrieved successfully: PASS

### Actual Console Output
```text
WRITE SUCCESS: Test point sent to InfluxDB.
READ SUCCESS: Test point retrieved.
humidity: 72.1
temperature: 28.4
```

## Security
- API token and password are not included in this log.
- Credentials are loaded from the project's `.env` file.
- `.env` must be excluded from Git using `.gitignore`.
- Never publish the API token in source code, screenshots, logs, or a public repository.
- The test script does not print the API token.

## Current Status
- InfluxDB OSS 2.9.1 installed and started successfully.
- Database storage configured on the D: drive.
- Organization and bucket configured.
- Custom API token created.
- Python client libraries installed successfully.
- Python write/read test completed successfully.
- Synthetic test data successfully written to and retrieved from InfluxDB.
- Documentation updated with the test results.

## Remaining Verification
- Confirm the bucket's retention period is set to 365 days.
- Confirm `.env` is ignored by Git using `git check-ignore .env`.
- Keep the InfluxDB server running when testing local database connectivity.

## Next Steps
- Integrate ESP32 telemetry with InfluxDB.
- Send actual sensor readings from the combined sensor firmware.
- Verify incoming temperature, humidity, vibration, water-level, and load-cell data.
- Develop a dashboard for real-time SHM monitoring.
- Add threshold-based alerts after validating sensor data quality.

## Day 18 Conclusion
InfluxDB was configured on the D: drive, and the Python-based database write/read test passed. The system is ready for the next stage of sensor telemetry integration, subject to the remaining retention and Git-ignore checks.
