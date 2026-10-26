# Day 13: Combined Firmware and Sensor Data Collection Log

## Objective
To integrate the DHT22, MPU6050, water sensor, and HX711 load-cell module with the ESP32 and collect combined sensor readings in JSON Lines format.

## Data Collection Summary
- Device ID: `ESP32-GW-LAB-001`
- Zone ID: `LAB_PROTOTYPE`
- First timestamp: 12,000 ms
- Last timestamp: 352,000 ms
- Number of records: 171
- Sampling interval: 2 seconds
- Elapsed time between first and last records: 5 minutes 40 seconds
- Output format: JSONL

## Sensor Observations
- **DHT22:** Temperature readings ranged from 31.5°C to 31.7°C. Humidity readings ranged from 92.5% to 93.6%.
- **MPU6050:** Acceleration and gyroscope readings were continuously recorded.
- **Water sensor:** ADC readings varied during collection, including zero and non-zero values. Further calibration is required to interpret the readings reliably.
- **Load cell/HX711:** Raw readings were recorded, but `load_kg` remained null because calibrated weight values were not available.

## Data Quality
All records contained `quality_flag: partial`. Therefore, the combined acquisition process produced sensor records, but the dataset should not yet be considered fully validated.

## Issues Requiring Follow-up
1. Calibrate the load cell using known reference weights and verify repeatability.
2. Investigate the cause of the varying HX711 raw readings.
3. Calibrate the water sensor against documented dry and wet conditions.
4. Validate the JSONL file programmatically and check for missing or malformed records.
5. Investigate why the firmware continues to mark every record as `partial`.

## Output File
`data/raw/combined_sensor_day13.jsonl`

## Status
Combined sensor data collection completed. Sensor calibration, data validation, and the cause of the persistent partial quality flag remain to be addressed.
