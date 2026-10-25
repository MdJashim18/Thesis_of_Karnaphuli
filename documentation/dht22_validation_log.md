
# Day 5 — DHT22 Sensor Validation and Data Collection

## 1. Objective

The objective of Day 5 is to validate the basic operation of the DHT22 temperature and relative humidity sensor connected to the ESP32, collect 100 readings at nominal 2-second intervals, examine data quality, and assess short-term reading variation.

## 2. Hardware Configuration

- Microcontroller: ESP32 DOIT DEVKIT V1
- Sensor: DHT22 temperature and relative humidity sensor
- Sensor data pin: GPIO 4
- Power connection: ESP32 3V3 to DHT22 VCC
- Ground connection: ESP32 GND to DHT22 GND
- Programming environment: Arduino IDE
- Serial Monitor baud rate: 115200

## 3. Data Collection Procedure

The DHT22 sensor was connected to the ESP32, and temperature and humidity readings were collected using the Arduino IDE Serial Monitor.

- Planned number of readings: 100
- Sampling interval: 2 seconds
- Nominal timestamp range: 0–198 seconds
- Data fields: timestamp, temperature, humidity
- Temperature unit: degrees Celsius (°C)
- Humidity unit: percent relative humidity (%RH)
- Raw data file: `data/raw/dht22_day5.csv`

Each CSV row is intended to contain a timestamp, temperature, and humidity reading. Invalid sensor values should be represented as `NaN` if returned by the sensor library.

The actual number of valid readings, invalid readings, and complete CSV rows must be verified from the saved dataset.

## 4. Data Collection Evidence

### 4.1 Sensor Setup Photograph

File: `hardware/photos/day5_sensor_setup.jpg`

This photograph documents the physical ESP32 and DHT22 setup and the wiring connections.

### 4.2 Serial Monitor Screenshot

File: `documentation/day5_serial_monitor.png`

This screenshot documents the temperature and humidity readings displayed in the Arduino IDE Serial Monitor.

### 4.3 Sensor Response Test

Files, if the test is performed:

- `hardware/photos/day5_response_test.jpg`
- `documentation/day5_breath_hand_test.png`

The photograph should document the actual test setup. The Serial Monitor screenshots should show readings before and after the test.

A response should only be reported if it is supported by the observed readings. This test does not independently establish sensor accuracy.

### 4.4 Temperature Context Photograph

File: `documentation/day5_reference_comparison.jpg`

The photograph shows the DHT22 setup, Serial Monitor, and temperature values displayed by a smartphone application.

The application displayed approximately 29.9°C for "Inside" and 31.3°C for "Outside", while the visible Serial Monitor readings were approximately 31.9°C.

These values are contextual observations only. The smartphone application's readings are not treated as measurements from an independent reference thermometer.

## 5. Statistical Analysis

The following statistics were calculated from the collected readings. The original CSV should be checked to confirm the calculations and the number of valid samples used.

### 5.1 Temperature Statistics

- Minimum temperature: 32.0°C
- Maximum temperature: 32.2°C
- Average temperature: 32.088°C (approximately 32.09°C)
- Temperature range: 0.2°C

Formula:

Temperature Range = Maximum Temperature − Minimum Temperature

Average Temperature = Sum of valid temperature readings / Number of valid temperature readings

### 5.2 Humidity Statistics

- Minimum relative humidity: 90.1%RH
- Maximum relative humidity: 91.5%RH
- Average relative humidity: 91.015%RH (approximately 91.02%RH)
- Humidity range: 1.4 percentage points

Formula:

Humidity Range = Maximum Humidity − Minimum Humidity

Average Humidity = Sum of valid humidity readings / Number of valid humidity readings

### 5.3 Data Quality

- Planned readings: 100
- Valid readings: Pending verification
- Invalid readings containing at least one NaN value: Pending verification
- Missing or incomplete CSV rows: Pending verification
- CSV column structure verified: Pending verification

A reading is considered invalid if either its temperature or humidity value is NaN. If both values are NaN in the same row, that row is counted as one invalid reading.

After verification:

Valid readings = Total readings − Invalid readings

The invalid-reading count must be taken from the actual data or firmware output, not estimated.

## 6. Short-Term Stability Assessment

The observed minimum-to-maximum ranges were:

- Temperature range: 0.2°C
- Relative humidity range: 1.4 percentage points

These values describe the variation reported for the collected readings during this test period.

A small observed range indicates that the readings varied within a narrow interval during the observation period. However, range alone does not establish measurement accuracy, calibration quality, or long-term reliability.

The final assessment remains subject to verification of the CSV data, valid-reading count, sampling sequence, and calculation method.

## 7. Reference Temperature Comparison

- Independent reference thermometer available: No
- Direct comparison with an independent reference thermometer: Not performed
- Contextual smartphone application readings documented: Yes, in the photograph
- Calibrated reference measurement available: No

### Limitation

The absolute temperature accuracy of the DHT22 has not been independently verified against a trusted reference instrument.

The smartphone application's displayed values are not considered a substitute for a reference thermometer under verified identical environmental conditions.

### Future Work

Repeat the temperature comparison using a trusted or calibrated thermometer placed near the DHT22 under the same environmental conditions. Record both instruments' readings and the time of measurement.

## 8. Limitations

1. The sensor was evaluated over a short observation period.
2. No independent reference thermometer was available.
3. Absolute temperature accuracy has not been independently verified.
4. Airflow, sensor placement, nearby heat sources, and local environmental conditions may affect readings.
5. Long-term reliability and calibration were not evaluated.
6. Data quality results remain pending until the saved CSV is verified.

## 9. Conclusion

The ESP32 DOIT DEVKIT V1 and DHT22 sensor were used to collect a planned set of 100 temperature and relative humidity readings at nominal 2-second intervals.

The reported temperature statistics were a minimum of 32.0°C, a maximum of 32.2°C, an average of approximately 32.09°C, and a range of 0.2°C.

The reported humidity statistics were a minimum of 90.1%RH, a maximum of 91.5%RH, an average of approximately 91.02%RH, and a range of 1.4 percentage points.

These statistics describe the reported observations and should be confirmed against the saved CSV data. The valid-reading count, invalid-reading count, and completeness of the dataset remain to be verified.

Because no independent reference thermometer was available, the absolute temperature accuracy of the sensor remains unverified.

## 10. Project Files

### Firmware

- `firmware/04_dht22_validation/04_dht22_validation.ino`

### Raw Data

- `data/raw/dht22_day5.csv`

### Hardware Photographs

- `hardware/photos/day5_sensor_setup.jpg`
- `hardware/photos/day5_response_test.jpg` (if captured)

### Documentation and Evidence

- `documentation/dht22_validation_log.md`
- `documentation/day5_serial_monitor.png`
- `documentation/day5_breath_hand_test.png` (if the response test is performed)
- `documentation/day5_reference_comparison.jpg`

### Calculations

- `documentation/dht22_day5_calculations.xlsx`

Only files that have actually been created should be considered completed project artifacts.

## 11. Completion Checklist

- [x] ESP32 and DHT22 connected
- [x] Serial Monitor screenshot captured
- [x] 100 readings collected, as reported
- [x] Temperature statistics calculated, as reported
- [x] Humidity statistics calculated, as reported
- [x] Reference-comparison limitation documented
- [ ] CSV structure and reading count verified
- [ ] Valid and invalid readings counted
- [ ] Missing or incomplete rows checked
- [ ] Statistical calculations cross-checked against the CSV
- [ ] Short-term stability assessment finalized
- [ ] Calculation results saved in the spreadsheet
- [ ] Final documentation reviewed

**Status:** Initial data collection and statistical calculations are reported as completed. CSV quality verification and final validation documentation remain pending.
