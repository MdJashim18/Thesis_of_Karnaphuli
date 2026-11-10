
# Data Acquisition and Processing Pipeline Log
## Karnaphuli Tunnel Real-Time Structural Health Monitoring Prototype

**Project:** Karnaphuli Tunnel Real-Time Maintenance Monitoring  
**Documentation Date:** 09 November 2026  
**Device ID:** ESP32-GW-LAB-001  
**Gateway ID:** gateway01  
**Zone ID:** LAB_PROTOTYPE  
**Session ID:** SHM-TEST-001  

---

## 1. Introduction

This document describes the data acquisition, communication,
processing, and storage pipeline developed for the
Karnaphuli Tunnel Real-Time Structural Health Monitoring
(SHM) prototype.

The system uses an ESP32 microcontroller to collect
measurements from multiple sensors.

The collected telemetry is transmitted through a Wi-Fi
network to a Python Flask HTTP API. The API processes
the incoming JSON payload and stores the sensor data
in InfluxDB.

In addition to database storage, the API maintains
local JSON Lines (JSONL) files for raw telemetry and
reliability-related records.

The main objective of this pipeline is to establish
a continuous and traceable sensor data acquisition
system for prototype monitoring and future research.

---

## 2. System Architecture

The implemented data acquisition pipeline consists
of the following stages:

1. Sensor data acquisition.
2. ESP32 firmware processing.
3. Wi-Fi communication.
4. HTTP POST transmission.
5. Python Flask API reception.
6. InfluxDB time-series storage.
7. Local JSONL data logging.
8. Dataset processing and analysis.

### 2.1 Data Flow

DHT22 ----------------\
MPU6050 ---------------\
Water Sensor ----------- > ESP32
Load Cell + HX711 ------/    |
                            |
                            v
                         Wi-Fi
                            |
                            v
                   Python Flask HTTP API
                       POST /telemetry
                            |
                 +----------+----------+
                 |                     |
                 v                     v
              InfluxDB             JSONL Files
                 |                     |
                 v                     v
          Data Explorer          Raw Data Analysis
                 |                     |
                 +----------+----------+
                            |
                            v
                  Visualization and
                   Reliability Analysis

### 2.2 Communication Architecture

The active implementation uses HTTP POST communication.

MQTT was also explored during project development,
but the current live data acquisition pipeline uses
the HTTP API.

Therefore, the results documented in this file refer
to the HTTP-based implementation.

---

## 3. Hardware Data Acquisition

The ESP32 collects measurements from four sensor groups.

### 3.1 DHT22 Temperature and Humidity Sensor

The DHT22 sensor measures environmental temperature
and relative humidity.

| Parameter | Description | Unit |
|---|---|---|
| temperature | Ambient temperature | °C |
| humidity | Relative humidity | % |
| dht_valid | Sensor validity status | Boolean |

ESP32 Pin:

- DATA: GPIO 4

### 3.2 MPU6050 Accelerometer

The MPU6050 provides three-axis acceleration readings.

| Parameter | Description |
|---|---|
| accel_x | X-axis acceleration |
| accel_y | Y-axis acceleration |
| accel_z | Z-axis acceleration |
| mpu_valid | Sensor validity status |

I2C configuration:

- SDA: GPIO 21
- SCL: GPIO 22
- I2C Address: 0x68

The acceleration readings are used as prototype
movement and vibration indicators.

Further signal processing is required before deriving
engineering-level structural vibration parameters.

### 3.3 Water Sensor

The HW-038 water sensor provides an analog output
connected to ESP32 GPIO 34.

| Parameter | Description |
|---|---|
| water_raw | Analog sensor reading |

The current implementation records raw analog readings.

The value is not directly interpreted as calibrated
water depth.

### 3.4 Load Cell and HX711

The load cell is connected to an HX711 amplifier.

| Parameter | Description |
|---|---|
| load_raw | Raw HX711 measurement |
| load_kg | Calculated load in kilograms |
| load_gram | Calculated load in grams |
| load_calibrated | Calibration activation status |
| hx711_valid | HX711 reading validity |

HX711 connections:

- DOUT: GPIO 18
- SCK: GPIO 19

The firmware applies a tare offset and calibration
factor to calculate the load measurement.

The current firmware stores calibration information
in ESP32 Preferences.

Latest calibration status:

- Offset: -610958
- Scale: 403550.000 raw/kg
- Tare: COMPLETED
- Calibration: ACTIVE

The above values represent the latest firmware
calibration record.

---

## 4. ESP32 Firmware Processing

The ESP32 firmware performs the following operations:

1. Initializes connected sensors.
2. Connects to the configured Wi-Fi network.
3. Synchronizes device time using NTP when available.
4. Reads sensor measurements.
5. Checks sensor validity.
6. Calculates calibrated load measurements.
7. Generates telemetry metadata.
8. Creates a JSON payload.
9. Sends the payload to the HTTP API.
10. Updates the transmission sequence after a
    successful HTTP response.

### 4.1 Device Metadata

The firmware includes the following metadata:

| Field | Description |
|---|---|
| device_id | ESP32 device identifier |
| gateway_id | Gateway identifier |
| zone_id | Prototype monitoring zone |
| session_id | Data collection session |
| sequence_number | Telemetry sequence |
| device_timestamp_ms | Device timestamp |
| wifi_reconnect_count | Wi-Fi reconnection counter |

### 4.2 Sensor Payload

The telemetry payload contains:

- temperature
- humidity
- accel_x
- accel_y
- accel_z
- water_raw
- load_raw
- load_kg
- load_gram

It also includes sensor validity and overall
data quality information.

---

## 5. Communication Layer

### 5.1 Wi-Fi Communication

The ESP32 uses a Wi-Fi network to communicate
with the computer hosting the Python API.

The API server runs on port 5000.

The ESP32 sends data to the configured host IP
address.

The host IP address must match the computer's
current local IPv4 address.

### 5.2 HTTP API Endpoint

HTTP method:

POST

Endpoint:

/telemetry

Example URL format:

http://HOST_IP:5000/telemetry

The actual host IP is configured in the ESP32 firmware.

### 5.3 HTTP Response

The Flask API returns an HTTP response after
processing the incoming telemetry request.

A successful request is indicated by:

HTTP 200 OK

During the captured test on 09 November 2026,
the Python terminal displayed repeated successful
POST requests.

Example:

"POST /telemetry HTTP/1.1" 200 -

This confirms that the API successfully handled
the corresponding HTTP requests.

---

## 6. Python Flask API

The backend API is implemented in:

python/http_ingest_api.py

The API uses Python and Flask to receive telemetry
from the ESP32.

### 6.1 Main Responsibilities

The API performs the following tasks:

1. Receives HTTP POST requests.
2. Parses incoming JSON telemetry.
3. Processes sensor and metadata fields.
4. Writes measurements to InfluxDB.
5. Maintains local telemetry JSONL records.
6. Maintains reliability-related log records.
7. Returns an HTTP response to the ESP32.

### 6.2 API Configuration

| Parameter | Value |
|---|---|
| Backend | Python Flask |
| API Port | 5000 |
| Route | /telemetry |
| HTTP Method | POST |
| Payload Format | JSON |
| Database Client | InfluxDB Python Client |

### 6.3 Local API Output Files

The API maintains the following local files:

**Raw telemetry:**

data/raw/continuous_24h.jsonl

**Reliability records:**

data/raw/reliability_log.jsonl

These files provide local records independently
of the database visualization interface.

---

## 7. InfluxDB Configuration

The project uses InfluxDB OSS for time-series
sensor data storage.

### 7.1 Database Configuration

| Parameter | Configuration |
|---|---|
| Database | InfluxDB OSS |
| Version | 2.9.1 |
| Organization | karnaphuli-lab |
| Bucket | tunnel_telemetry |
| Retention Period | 365 days |
| Measurement | tunnel_telemetry |

InfluxDB stores timestamped measurements and
associated device metadata.

### 7.2 Stored Sensor Fields

| Field | Description |
|---|---|
| temperature | Temperature in Celsius |
| humidity | Relative humidity |
| accel_x | X-axis acceleration |
| accel_y | Y-axis acceleration |
| accel_z | Z-axis acceleration |
| water_raw | Water sensor raw reading |
| load_raw | HX711 raw reading |
| load_kg | Calculated load in kilograms |
| load_gram | Calculated load in grams |
| load_calibrated | Load calibration status |
| dht_valid | DHT sensor validity |
| mpu_valid | MPU sensor validity |
| hx711_valid | HX711 sensor validity |
| quality_flag | Overall telemetry quality |

The exact fields visible in an InfluxDB query
depend on the selected measurement, time range,
and field filters.

### 7.3 Data Explorer Verification

InfluxDB Data Explorer was used to inspect the
stored sensor measurements.

The captured database screenshot dated
09 November 2026 shows sensor fields including:

- temperature
- humidity
- accel_x
- accel_y
- accel_z
- water_raw
- load_raw
- load_kg
- quality_flag

An example displayed load measurement was:

load_kg = 0.20381

The corresponding raw measurement was:

load_raw = -528712

The displayed quality flag was:

quality_flag = ok

These values demonstrate that a non-zero load
measurement was stored in InfluxDB during the
captured prototype test.

These are laboratory prototype readings and
must not be interpreted as actual tunnel
structural measurements.

---

## 8. JSONL Dataset and Local Data Logging

### 8.1 Primary Raw Dataset

The primary continuous telemetry dataset is:

data/raw/continuous_24h.jsonl

The file uses JSON Lines (JSONL) format.

Each line contains one individual JSON telemetry
record.

Unlike a conventional JSON array, JSONL stores
multiple independent JSON objects, one per line.

### 8.2 Dataset Contents

The telemetry records may contain:

- session_id
- sequence_number
- received_at
- device_timestamp_ms
- latency_ms
- latency_valid
- wifi_reconnect_count
- device_id
- gateway_id
- zone_id
- temperature
- humidity
- accel_x
- accel_y
- accel_z
- water_raw
- load_raw
- load_kg
- load_gram
- load_calibrated
- dht_valid
- mpu_valid
- hx711_valid
- quality_flag

The exact fields depend on the JSONL record
schema written by the API.

### 8.3 JSONL Storage Advantages

JSONL was selected for local telemetry logging
because it provides:

1. One-record-per-line storage.
2. Easy append-based logging.
3. Convenient processing with Python.
4. Preservation of individual telemetry records.
5. Support for large continuous data collections.
6. Easy conversion into CSV or other analysis formats.

### 8.4 Dataset Processing

The JSONL dataset can be processed using Python
and Pandas.

Typical processing operations include:

- JSON parsing
- Timestamp conversion
- Missing value detection
- Duplicate record detection
- Sequence gap analysis
- Sensor value validation
- Statistical analysis
- Visualization
- CSV export

The original JSONL file should be preserved as
the raw dataset.

Any cleaned or transformed dataset should be
stored separately.

### 8.5 Dataset Evidence

The following evidence should be preserved:

- JSONL file preview showing actual records.
- Dataset field names.
- Multiple consecutive telemetry records.
- File size and total record count.
- Data collection start and end timestamps.

Recommended screenshot:

evidence/dataset/continuous_24h_jsonl_preview.png

---

## 9. Data Quality Monitoring

The firmware and backend use data quality
indicators to describe telemetry validity.

### 9.1 Quality Flags

| Quality Flag | Description |
|---|---|
| ok | Required sensor readings valid and load calibration active |
| partial | Telemetry available but calibration or another required condition is incomplete |
| degraded | One or more required sensor readings are invalid |

The exact classification depends on the
firmware quality-checking logic.

### 9.2 Sensor Validity

The following indicators are included:

- dht_valid
- mpu_valid
- hx711_valid
- load_calibrated

These fields help distinguish valid measurements
from incomplete or potentially unreliable readings.

### 9.3 Data Quality Considerations

A quality flag does not independently prove
measurement accuracy.

For example, a load cell can be calibrated
and report valid readings while still having
a measurement error at higher loads.

Therefore, sensor calibration and independent
validation remain necessary.

---

## 10. Reliability Logging

The reliability log is maintained at:

data/raw/reliability_log.jsonl

The log is intended to preserve information
about data reception and communication reliability.

Depending on the fields recorded by the API,
the reliability analysis may include:

- Expected readings
- Received readings
- Missing readings
- Sequence gaps
- Reception timestamps
- Latency measurements
- Latency validity
- Wi-Fi reconnection events
- Data collection duration

### 10.1 Latency

When both device and reception timestamps are
available and synchronized, transmission latency
can be estimated.

Latency:

latency_ms = received_at - device_timestamp_ms

The actual calculation must account for
timestamp units and clock synchronization.

Invalid or unsynchronized timestamps should
not be included in valid latency statistics.

### 10.2 Data Completeness

Data completeness can be calculated as:

Data Completeness (%) =
(Received Readings / Expected Readings) × 100

Missing Readings =
Expected Readings - Received Readings

These metrics must be calculated from the
actual collection records.

No estimated values should be reported as
measured reliability results.

---

## 11. Data Export and Analysis

The original telemetry is stored in JSONL format.

For statistical analysis, the JSONL file can
be transformed into a tabular dataset.

Potential output:

data/cleaned/month2_final_dataset.csv

This CSV file is an optional processed output.
It should only be listed as completed after
the conversion has actually been performed
and the output file has been verified.

Potential analysis includes:

- Descriptive statistics
- Sensor time-series plots
- Missing data analysis
- Latency distribution
- Communication reliability
- Load measurement validation
- Anomaly detection
- Future machine learning experiments

The original JSONL dataset must remain unchanged
during cleaning and transformation.

---

## 12. Database Query

The following Flux query can be used to inspect
recent sensor measurements in InfluxDB.

    from(bucket: "tunnel_telemetry")
      |> range(start: -30m)
      |> filter(fn: (r) =>
          r._measurement == "tunnel_telemetry"
      )
      |> filter(fn: (r) =>
          r._field == "temperature" or
          r._field == "humidity" or
          r._field == "accel_x" or
          r._field == "accel_y" or
          r._field == "accel_z" or
          r._field == "water_raw" or
          r._field == "load_raw" or
          r._field == "load_kg" or
          r._field == "load_gram"
      )
      |> sort(columns: ["_time"], desc: true)

The time range can be modified to inspect
a longer collection period.

---

## 13. Pipeline Verification Results

Based on the captured prototype evidence:

| Component | Verification Status |
|---|---|
| ESP32 sensor acquisition | Operational during captured test |
| DHT22 readings | Observed |
| MPU6050 readings | Observed |
| Water sensor readings | Observed |
| HX711 raw readings | Observed |
| Load cell calibration | Active |
| Non-zero load calculation | Observed |
| Wi-Fi communication | Successful during captured test |
| Python Flask API | Operational during captured test |
| HTTP POST transmission | HTTP 200 responses observed |
| InfluxDB storage | Verified through Data Explorer |
| JSONL local logging | Project output configured |
| Reliability analysis | Requires final log-based calculation |
| MQTT end-to-end pipeline | Not verified by current evidence |
| CSV processed dataset | Optional; verify file before claiming completion |
| 24–48-hour continuous test | Requires duration and completeness verification |

---

## 14. Evidence and Screenshots

The following evidence should be included
with the project documentation.

### 14.1 Hardware Evidence

Location:

evidence/hardware/

Recommended files:

- complete_hardware_prototype.jpg
- esp32_board_closeup.jpg
- loadcell_hx711_wiring.jpg
- environmental_imu_sensor_wiring.jpg
- water_sensor_setup.jpg

### 14.2 Firmware Evidence

Location:

evidence/firmware/

Recommended file:

- esp32_live_sensor_output.png

The screenshot should show sensor values,
load measurements, and transmission status.

### 14.3 Communication Evidence

Location:

evidence/communication/

Recommended file:

- python_http_api_success_2026-11-09.png

This screenshot should show successful
HTTP POST responses.

### 14.4 Database Evidence

Location:

evidence/database/

Recommended files:

- influxdb_sensor_data_2026-11-09.png
- influxdb_sensor_timeseries.png

### 14.5 Dataset Evidence

Location:

evidence/dataset/

Recommended file:

- continuous_24h_jsonl_preview.png

The screenshot should show the actual JSONL
records, including metadata and sensor fields.

### 14.6 Reliability Evidence

Location:

evidence/reliability/

Recommended files:

- temperature_timeseries.png
- humidity_timeseries.png
- acceleration_timeseries.png
- load_timeseries.png
- water_sensor_timeseries.png
- reliability_summary.png

These files should be generated from actual
collected data.

---

## 15. Current Limitations

The current system is a laboratory-scale
prototype and has several limitations.

1. Sensor measurements have not yet been
   validated against actual tunnel instrumentation.

2. Water sensor readings are raw analog values
   and are not calibrated water-depth measurements.

3. MPU6050 acceleration data requires further
   filtering and vibration analysis.

4. Load cell validation showed good performance
   at 100 g, 200 g, and 500 g, but a significant
   error at 1000 g in the earlier validation test.

5. A complete 24–48-hour reliability result
   must be calculated from the actual logs.

6. MQTT end-to-end operation is not confirmed
   by the current HTTP pipeline evidence.

7. The current prototype does not directly
   establish the structural safety condition
   of the Karnaphuli Tunnel.

---

## 16. Future Development

Future development activities include:

- Longer continuous data collection.
- Improved sensor calibration.
- Sensor noise filtering.
- Vibration feature extraction.
- Anomaly detection.
- Explainable AI-based interpretation.
- Maintenance alert generation.
- Time-series visualization.
- Generalization to other tunnel environments.

The long-term goal is to develop an explainable
real-time maintenance monitoring framework
that can support tunnel infrastructure
monitoring and decision-making.

---

## 17. Conclusion

The implemented pipeline integrates ESP32-based
sensor acquisition, Wi-Fi communication,
Python Flask HTTP API, InfluxDB time-series
storage, and local JSONL data logging.

The captured test evidence confirms successful
HTTP telemetry reception and InfluxDB storage
of multiple sensor measurements, including
calculated load cell values.

The continuous_24h.jsonl file serves as the
primary raw telemetry dataset for subsequent
data processing, reliability analysis,
visualization, and research.

This pipeline provides the foundation for
future development of a real-time and explainable
Structural Health Monitoring system for
tunnel maintenance applications.
