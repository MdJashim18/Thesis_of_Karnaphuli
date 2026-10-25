# DHT22 Sensor Setup Log

## Project
Karnaphuli Tunnel Structural Health Monitoring (SHM) — Month 2

## Experiment
ESP32 with DHT22 Temperature and Humidity Sensor

## Hardware
- ESP32 DOIT DEVKIT V1
- DHT22 temperature and humidity sensor
- USB cable
- Jumper wires

## Software
- Arduino IDE
- Adafruit DHT Sensor Library
- Adafruit Unified Sensor Library

## Implementation
1. Connected ESP32 to the computer using USB.
2. Selected the DOIT ESP32 DEVKIT V1 board.
3. Selected the correct COM port.
4. Compiled and uploaded the firmware successfully.
5. Opened the Serial Monitor to observe sensor readings.

## Observed Results
- Temperature: approximately 32.0 °C
- Relative humidity: approximately 93.2%–93.3%
- Sensor readings changed during observation.

## Status
SUCCESS — Temperature and humidity readings received through the Serial Monitor.

## Notes
These are initial sensor readings. Further testing and calibration may be needed.

## Evidence
- Wiring diagram: `hardware/wiring_diagram/03_dht22_esp32.png`
- Hardware photo: `hardware/photos/dht22_wiring.jpg`
- Firmware: `firmware/03_dht22/03_dht22.ino`