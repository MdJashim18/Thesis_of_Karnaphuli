# Hardware Setup and Testing Log
## Karnaphuli Tunnel Real-Time Structural Health Monitoring Prototype

**Project:** Karnaphuli Tunnel Real-Time Maintenance Monitoring  
**Platform:** ESP32-based IoT Structural Health Monitoring Prototype  
**Device ID:** ESP32-GW-LAB-001  
**Gateway ID:** gateway01  
**Zone ID:** LAB_PROTOTYPE  
**Session ID:** SHM-TEST-001  
**Documentation Date:** 09 November 2026

---

## 1. Project Overview

This project develops an IoT-based Structural Health Monitoring (SHM)
prototype for real-time monitoring of tunnel-related environmental
and physical parameters.

The prototype uses an ESP32 microcontroller connected to multiple
sensors. Sensor readings are transmitted to a Python-based HTTP API
and stored in InfluxDB for monitoring, analysis, and future
maintenance decision-support development.

The current prototype focuses on:

- Temperature monitoring
- Humidity monitoring
- Vibration and acceleration monitoring
- Water presence / water-level indication
- Load measurement
- Continuous sensor data collection
- Data transmission reliability

---

## 2. Hardware Components

| Component | Purpose |
|---|---|
| ESP32 DevKit V1 | Main microcontroller |
| DHT22 | Temperature and humidity measurement |
| MPU6050 | Acceleration and vibration measurement |
| HW-038 Water Sensor | Water detection / analog response |
| HX711 | Load cell signal amplifier and ADC |
| Load Cell | Weight / load measurement |
| Jumper Wires | Electrical connections |
| Breadboard / Prototype Platform | Circuit assembly |
| USB Cable | Power and serial communication |

---

## 3. ESP32 Pin Configuration

| Sensor | ESP32 Pin | Function |
|---|---|---|
| DHT22 DATA | GPIO 4 | Digital data |
| MPU6050 SDA | GPIO 21 | I2C data |
| MPU6050 SCL | GPIO 22 | I2C clock |
| Water Sensor AO | GPIO 34 | Analog input |
| HX711 DOUT | GPIO 18 | Data output |
| HX711 SCK | GPIO 19 | Clock input |

### I2C Configuration

- MPU6050 I2C Address: 0x68
- SDA: GPIO 21
- SCL: GPIO 22

---

## 4. Sensor Configuration

### 4.1 DHT22

The DHT22 sensor measures:

- Temperature in Celsius
- Relative humidity in percentage

Firmware variables:

- temperature
- humidity
- dht_valid

### 4.2 MPU6050

The MPU6050 sensor provides acceleration measurements
along three axes.

Firmware variables:

- accel_x
- accel_y
- accel_z
- mpu_valid

The acceleration values are used as prototype vibration /
movement indicators.

### 4.3 Water Sensor

The HW-038 analog output is connected to GPIO 34.

Firmware variable:

- water_raw

The analog reading represents the sensor's raw response.
It is not yet a calibrated water depth measurement.

### 4.4 Load Cell and HX711

The load cell is connected to the HX711 amplifier.

HX711 connections:

- DOUT: GPIO 18
- SCK: GPIO 19

Firmware variables:

- load_raw
- load_kg
- load_gram
- load_calibrated
- hx711_valid

The load cell is calibrated using a known reference weight.
The tare offset and calibration factor are stored in ESP32
Preferences.

---

## 5. Prototype Device Configuration

| Parameter | Value |
|---|---|
| Microcontroller | ESP32 DOIT DevKit V1 |
| ESP32 Chip | ESP32-D0WD-V3 |
| Firmware Environment | Arduino IDE |
| Serial Baud Rate | 115200 |
| Wi-Fi Network | Bachelor |
| Communication | HTTP POST |
| API Endpoint | /telemetry |
| API Port | 5000 |
| Database | InfluxDB OSS 2.9.1 |
| Database Bucket | tunnel_telemetry |

The API server IP address should be verified from the host
computer before starting data collection.

---

## 6. Hardware Testing Results

The following observations were obtained during prototype testing:

- ESP32 successfully communicates with the connected sensors.
- DHT22 provides temperature and humidity readings.
- MPU6050 provides three-axis acceleration readings.
- Water sensor provides analog raw readings.
- HX711 provides load cell raw readings.
- Load cell calibration has been activated.
- Load measurements are successfully transmitted to the API.
- InfluxDB stores the sensor readings.

The InfluxDB screenshot dated 09 November 2026 shows:

- Temperature: approximately 26.9–27.0 °C
- Humidity: approximately 78.2–78.8%
- Acceleration values on X, Y, and Z axes
- Load measurements including approximately 0.20381 kg
- Water sensor raw reading: 0 in the displayed records
- Quality flag: ok

These values represent the displayed prototype test readings,
not actual Karnaphuli Tunnel measurements.

---

## 7. Hardware Evidence

The following photographs should be stored in the evidence folder:

1. Complete ESP32 prototype.
2. ESP32 board close-up.
3. DHT22 wiring.
4. MPU6050 wiring.
5. Water sensor wiring.
6. Load cell and HX711 wiring.
7. Complete sensor connection overview.

Recommended image directory:

evidence/hardware/

---

## 8. Limitations

- The prototype is a laboratory-scale experimental setup.
- The HW-038 sensor is not a calibrated tunnel water-depth sensor.
- MPU6050 acceleration readings require further filtering and
  vibration analysis.
- Load cell measurements depend on mechanical mounting,
  calibration, and applied load position.
- The prototype readings do not represent actual structural
  conditions inside the Karnaphuli Tunnel.

---

## 9. Conclusion

The ESP32-based hardware prototype successfully integrates
temperature, humidity, acceleration, water detection, and load
measurement sensors.

The hardware is connected to a Python HTTP API and InfluxDB
for continuous data acquisition and storage.

Further work will focus on long-duration reliability testing,
sensor validation, signal processing, anomaly detection,
and explainable maintenance decision support.