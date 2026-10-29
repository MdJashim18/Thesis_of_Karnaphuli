# Day 21: HTTP API Reliability and Recovery Test Log

## Project Information
- Project: Karnaphuli Tunnel Structural Health Monitoring (SHM)
- Device: ESP32
- Communication: HTTP API over Wi-Fi
- Monitoring: Live sensor dashboard
- Test Date: 2026-10-28

## Objective
To evaluate the recovery of live sensor telemetry after Wi-Fi disconnection and HTTP API server restart.

The current prototype uses HTTP API communication. Therefore, Mosquitto and MQTT-specific tests are excluded from this experiment.

## System Architecture
ESP32 Sensors → Wi-Fi → HTTP API Server → Live Dashboard

Sensors:
- DHT22 temperature and humidity sensor
- MPU6050 accelerometer and gyroscope
- Water sensor
- HX711 load-cell module

## Test 1: Wi-Fi Disconnection and Reconnection

### Procedure
1. Confirm that live sensor readings are displayed on the dashboard.
2. Disconnect Wi-Fi while keeping the ESP32 powered.
3. Observe the dashboard during the disconnection.
4. Restore Wi-Fi and check whether telemetry resumes.

### Observed Results
- Dashboard updates stopped during Wi-Fi disconnection.
- After Wi-Fi was restored, live sensor data resumed.
- The exact recovery time was not recorded.

### Status
**PASS — live telemetry recovered after Wi-Fi reconnection.**

## Test 2: HTTP API Server Restart and Recovery

### Procedure
1. Confirm that the dashboard is receiving live sensor data.
2. Stop the HTTP API server using Ctrl+C.
3. Restart the API server using the usual command.
4. Keep the ESP32 powered and do not press the EN button.
5. Record the time until dashboard data returns.

### Experimental Results

| Trial | Recovery Time | EN Button Pressed? |
|---|---:|---|
| 1 | 20 seconds | No |
| 2 | 25 seconds | No |
| 3 | 28 seconds | No |

### Average Recovery Time

Average recovery time = (20 + 25 + 28) / 3

**Average = 24.33 seconds**

### Observation
In all three reported trials, live telemetry returned to normal without manually pressing the ESP32 EN button. The observed recovery time ranged from 20 to 28 seconds.

### Status
**PASS — recovery observed in all three trials.**

## Test 3: Separate ESP32 Reboot Test

A separate, controlled ESP32 reboot test has not yet been independently documented.

### Required Procedure
1. Keep the HTTP API server running.
2. Confirm that the dashboard is receiving live data.
3. Press the ESP32 EN button once.
4. Observe whether the ESP32 reconnects to Wi-Fi.
5. Check whether HTTP telemetry resumes without additional manual intervention.
6. Record the recovery time and outcome.

### Status
**PENDING — separate ESP32 reboot test required.**

## Scope and Limitations
- This experiment evaluates HTTP API and Wi-Fi recovery.
- No Mosquitto broker restart test was performed.
- No wrong-MQTT-password authentication test was performed.
- MQTT-specific reliability was not evaluated because the current implementation uses HTTP API communication.
- Recovery times are based on observed results, not automated timestamp measurements.
- This experiment does not verify whether sensor readings missed during a disconnection are buffered or replayed.
- Results apply to the laboratory prototype and do not constitute field validation of the Karnaphuli Tunnel.

## Conclusion
The HTTP API prototype recovered after Wi-Fi reconnection. Following three HTTP API server restart trials, live telemetry resumed in approximately 20, 25, and 28 seconds without pressing the ESP32 EN button.

The mean observed recovery time across these three trials was approximately 24.33 seconds.

A separate ESP32 reboot test remains to be completed and documented.