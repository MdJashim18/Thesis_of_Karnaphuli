# MQTT Communication Test Log
## Karnaphuli Tunnel Real-Time Structural Health Monitoring Prototype

**Project:** Karnaphuli Tunnel Real-Time Maintenance Monitoring  
**Documentation Date:** 09 November 2026

---

## 1. Objective

The objective of this log is to document the MQTT communication
setup and testing activities for the ESP32-based SHM prototype.

MQTT was considered as a lightweight messaging protocol for
transmitting sensor telemetry from the ESP32 gateway to a
centralized data collection service.

---

## 2. MQTT Environment

| Parameter | Configuration |
|---|---|
| MQTT Broker | Eclipse Mosquitto |
| Broker Version | 2.1.2 |
| Operating System | Windows |
| Broker Address | localhost / 127.0.0.1 |
| Default MQTT Port | 1883 |
| MQTT Username | sensor_user |
| Telemetry Topic | karnaphuli/tunnel/+/+/telemetry |

The Mosquitto installation directory was:

D:\Software\Mosquitto

---

## 3. MQTT Topic Structure

Configured telemetry topic:

karnaphuli/tunnel/+/+/telemetry

The topic structure supports device and zone-specific
telemetry organization.

The wildcard symbols allow the subscriber to receive
messages from multiple tunnel zones and devices.

---

## 4. MQTT Data Fields

The telemetry structure was designed to support:

- device_id
- gateway_id
- zone_id
- session_id
- sequence_number
- device_timestamp_ms
- temperature
- humidity
- accel_x
- accel_y
- accel_z
- water_raw
- load_raw
- load_kg
- load_gram
- quality_flag

---

## 5. MQTT Broker Configuration

Mosquitto was installed and configured on the Windows
development computer.

The MQTT broker was configured to support authenticated
connections.

Broker and subscriber configuration should be verified
before conducting a new end-to-end MQTT experiment.

---

## 6. Current Communication Architecture

The active prototype data collection pipeline uses HTTP
rather than MQTT.

Current data flow:

ESP32
  |
  v
Wi-Fi Network
  |
  v
Python Flask HTTP API
  |
  v
InfluxDB
  |
  v
Data Explorer / Analysis

The ESP32 sends telemetry through:

POST /telemetry

The Python API receives the JSON payload and stores the
sensor measurements in InfluxDB.

---

## 7. MQTT vs HTTP

| Feature | MQTT | HTTP |
|---|---|---|
| Communication Model | Publish/Subscribe | Request/Response |
| Broker Required | Yes | No |
| Current Prototype | Not active | Active |
| Data Endpoint | MQTT topic | /telemetry |
| Current Evidence | Configuration history | HTTP 200 responses |

---

## 8. Test Status and Evidence

Mosquitto installation and MQTT topic configuration were
part of the project development.

However, the currently supplied evidence confirms successful
HTTP telemetry transmission, not a complete MQTT-to-InfluxDB
end-to-end test.

Therefore, MQTT end-to-end functionality is marked as
pending independent verification.

Recommended future evidence:

1. Mosquitto broker running screenshot.
2. MQTT publisher connection screenshot.
3. MQTT subscriber terminal output.
4. Received telemetry JSON message.
5. MQTT-to-database integration result, if implemented.

---

## 9. Conclusion

MQTT was evaluated as a communication option for the
ESP32-based SHM system.

The active data collection implementation currently uses
HTTP POST requests through a Python Flask API.

MQTT remains a documented communication option and should
be considered separately from the verified HTTP pipeline.