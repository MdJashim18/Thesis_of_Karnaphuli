# Troubleshooting and Issue Resolution Log
## Karnaphuli Tunnel Real-Time Structural Health Monitoring Prototype

**Documentation Date:** 09 November 2026

---

## 1. Overview

This document records the major technical issues encountered
during the development and testing of the ESP32-based
Structural Health Monitoring prototype.

The purpose is to maintain a technical history of problems,
their possible causes, troubleshooting steps, and current status.

---

## 2. Wi-Fi Connection Problems

### Problem

ESP32 sometimes failed to connect to the configured
Wi-Fi network.

Observed messages included:

- Wi-Fi connection failed.
- STA is connecting, cannot set config.
- Reconnection attempts.

### Possible Causes

- Incorrect Wi-Fi credentials.
- Weak Wi-Fi signal.
- Router connection instability.
- Reconfiguration while ESP32 was already connecting.
- Temporary network interruption.

### Resolution

The Wi-Fi connection procedure was reviewed and tested again.

The ESP32 successfully connected to the network during
the later HTTP telemetry test.

### Status

Operational during the captured test.

---

## 3. HTTP API Connection Problems

### Problem

The ESP32 previously experienced HTTP connection failures.

Observed errors included:

- HTTP 403
- Connection refused

### Possible Causes

- Incorrect API host IP address.
- Flask server not running.
- Incorrect endpoint.
- Network firewall restrictions.
- Client and server not connected to the same network.

### Resolution

The host computer's local IPv4 address was checked.

The firmware API URL was configured to use the current
host IP address and port 5000.

The Flask API was started before transmitting telemetry.

### Verification

The Python terminal subsequently showed repeated:

POST /telemetry HTTP/1.1 200

### Status

HTTP telemetry transmission was successful in the
09 November 2026 test.

---

## 4. Load Cell Calibration Problem

### Problem

Initially, the HX711 raw values reached the backend,
but load_kg remained zero.

### Cause

The load cell calibration state was inactive.

The firmware could transmit raw readings without calculating
the actual weight.

### Resolution

The firmware calibration procedure was improved.

The following calibration states were introduced:

- tareCompleted
- loadCalibrated
- loadOffset
- loadScale

Calibration information is stored using ESP32 Preferences.

### Current Calibration Status

Offset: -610958

Scale: 403550.000 raw/kg

Tare: COMPLETED

Calibration: ACTIVE

### Verification

The latest InfluxDB screenshot shows:

load_kg = 0.20381

load_raw = -528712

quality_flag = ok

### Status

Load cell weight calculation and database transmission
are operational during the captured test.

---

## 5. Load Cell Validation Error

### Problem

The load cell produced accurate measurements at lower
reference weights but showed a significant error at 1000 g.

### Validation Results

| Reference Weight | Mean Measured | Mean Absolute Error |
|---|---:|---:|
| 100 g | 99.363 g | 0.637% |
| 200 g | 200.249 g | 0.184% |
| 500 g | 501.252 g | 0.250% |
| 1000 g | 861.954 g | 13.805% |

### Possible Causes

- Mechanical mounting problems.
- Uneven load distribution.
- Load cell non-linearity.
- Electrical noise.
- Reference weight uncertainty.
- Mechanical contact or friction.

### Recommended Action

Inspect the mechanical installation and repeat the
1000 g validation test.

Do not claim full-range measurement accuracy until
the issue has been investigated.

### Status

Lower-weight validation is satisfactory in the reported
experiment. The 1000 g range requires further testing.

---

## 6. InfluxDB Data Verification

### Problem

Initially, it was difficult to determine whether all
sensor values were being stored correctly.

### Resolution

InfluxDB Data Explorer was used to inspect recent
measurements.

The following fields were observed:

- temperature
- humidity
- accel_x
- accel_y
- accel_z
- water_raw
- load_raw
- load_kg
- quality_flag

### Verification

The latest screenshot shows non-zero load measurements
and quality_flag = ok.

### Status

Database storage verified for the displayed fields.

---

## 7. Water Sensor Reading

### Observation

The latest InfluxDB screenshot shows:

water_raw = 0

### Interpretation

This is the raw analog reading recorded during the
displayed sample.

It may indicate a dry sensor condition, but the raw
value alone does not establish calibrated water depth.

### Recommended Action

Perform dry and wet sensor tests and record the raw
readings under controlled conditions.

Use a separate calibration procedure before converting
raw readings into water depth.

---

## 8. Data Quality Status

The firmware uses quality flags to identify the
overall condition of telemetry.

| Quality Flag | Interpretation |
|---|---|
| ok | Required sensor readings valid and calibration active |
| partial | Telemetry available with incomplete calibration or another required condition |
| degraded | One or more required sensor readings invalid |

The latest InfluxDB screenshot shows:

quality_flag = ok

---

## 9. MQTT and HTTP Communication

The project initially considered MQTT communication
using Mosquitto.

The active implementation currently uses HTTP POST
through the Python Flask API.

The successful HTTP 200 responses verify the active
HTTP pipeline.

A separate end-to-end MQTT test is still required
before claiming MQTT pipeline completion.

---

## 10. Summary of Issues

| Issue | Current Status |
|---|---|
| Wi-Fi connection | Operational during captured test |
| HTTP connection | Resolved for captured test |
| HTTP 403 / connection refused | Previously observed; successful HTTP 200 afterward |
| Load cell zero output | Resolved through calibration activation |
| Load cell weight transmission | Verified in InfluxDB |
| 1000 g validation error | Requires further investigation |
| Water sensor calibration | Further validation required |
| MQTT end-to-end verification | Pending |
| InfluxDB storage | Verified |

---

## 11. Conclusion

Several hardware, communication, calibration, and data
storage issues were encountered during prototype development.

The ESP32-to-HTTP-API-to-InfluxDB pipeline is now
operational in the captured test.

Load cell calibration is active and non-zero weight
measurements are visible in InfluxDB.

Further work is required for higher-load calibration,
water sensor validation, MQTT verification, and
long-duration reliability analysis.