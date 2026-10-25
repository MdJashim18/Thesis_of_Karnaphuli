# Day 5 — DHT22 Sensor Validation and Data Collection

## 1. Objective

The objective was to collect DHT22 temperature and relative-humidity readings using an ESP32, inspect data quality, calculate descriptive statistics, and assess short-term variation.

## 2. Hardware Configuration

- Microcontroller: ESP32 DOIT DEVKIT V1
- Sensor: DHT22 temperature and relative humidity sensor
- Data pin: GPIO 4
- Supply: ESP32 3V3 to DHT22 VCC
- Ground: ESP32 GND to DHT22 GND
- Programming environment: Arduino IDE
- Serial Monitor baud rate: 115200

## 3. Data Collection and Timestamp Verification

- Planned readings: 100
- Rows in the output supplied for review: 99
- Sampling interval: 2 seconds
- First timestamp in supplied output: 2 seconds
- Last timestamp in supplied output: 198 seconds
- Timestamp intervals: all consecutive rows are 2 seconds apart
- CSV columns: `timestamp`, `temperature`, `humidity`
- Reviewed data file: `data/raw/dht22_day5.csv`

**Important discrepancy:** The supplied output contains 99 data rows, with timestamps 2 through 198. It does not contain a timestamp-0 row. Therefore, the stated goal of 100 readings is not confirmed by this output. Check the original CSV and Serial Monitor log before marking the 100-reading requirement complete.

## 4. Data Collection Evidence

- Sensor setup photograph: `hardware/photos/day5_sensor_setup.jpg`
- Serial Monitor screenshot: `documentation/day5_serial_monitor.png`
- Contextual smartphone display photograph: `documentation/day5_reference_comparison.jpg`

The response-test photo and before/after screenshots should only be listed as completed evidence if that test was actually performed and the files were saved.

## 5. Statistical Analysis

Statistics below are calculated from the 99 data rows pasted for review. They should be checked against the actual saved CSV if it differs from the pasted output.

### 5.1 Temperature Statistics

- Minimum temperature: 32.0°C
- Maximum temperature: 32.2°C
- Average temperature: 32.0879°C (approximately 32.09°C)
- Temperature range: 0.2°C

Formula: `Temperature range = maximum temperature − minimum temperature`

Formula: `Average temperature = sum of valid temperature readings / number of valid temperature readings`

### 5.2 Humidity Statistics

- Minimum relative humidity: 90.1%RH
- Maximum relative humidity: 91.5%RH
- Average relative humidity: 91.0152%RH (approximately 91.02%RH)
- Humidity range: 1.4 percentage points

Formula: `Humidity range = maximum humidity − minimum humidity`

Formula: `Average humidity = sum of valid humidity readings / number of valid humidity readings`

## 6. Data Quality

- Data rows reviewed: 99
- Valid readings in supplied output: 99
- Invalid readings containing a missing or NaN temperature/humidity value: 0
- Missing or incomplete rows observed in supplied output: 0
- Timestamp interval consistency: Passed (2 seconds between each consecutive row)
- Planned 100-reading count: Not met by the supplied output; one reading is missing relative to the plan

A reading is invalid if either temperature or humidity is missing or NaN. If both are invalid in one row, that row is counted once. No such rows were present in the supplied output.

## 7. Short-Term Stability Assessment

- Temperature range: 0.2°C
- Relative-humidity range: 1.4 percentage points

The readings stayed within these observed ranges during the supplied observation period. This describes short-term variation only; it does not establish calibration, absolute accuracy, or long-term reliability.

## 8. Reference Temperature Comparison

- Independent reference thermometer available: No
- Direct comparison with an independent reference thermometer: Not performed
- Smartphone application values visible in the photograph: 29.9°C ("Inside") and 31.3°C ("Outside")
- Approximate DHT22 value visible in the photograph: 31.9°C

The smartphone application's displayed values are contextual observations, not a verified reference-thermometer measurement. Absolute sensor accuracy has not been independently verified.

## 9. Limitations

1. Only 99 rows were present in the supplied output, despite the plan for 100 readings.
2. The observation period was short.
3. No independent reference thermometer was used.
4. Environmental factors such as airflow, sensor placement, and nearby heat sources may affect readings.
5. Long-term reliability and calibration were not assessed.

## 10. Conclusion

The supplied DHT22 output contains 99 valid temperature and humidity readings with timestamps from 2 to 198 seconds at consistent 2-second intervals. No missing or NaN temperature/humidity values were found in these rows.

The average temperature was approximately 32.09°C, with a range of 0.2°C. The average relative humidity was approximately 91.02%RH, with a range of 1.4 percentage points.

The supplied output does not confirm completion of the planned 100 readings because the timestamp-0 row is absent. Review the original CSV/Serial Monitor output and collect or recover the missing reading if available. A reference thermometer comparison was not performed, so absolute temperature accuracy remains unverified.

## 11. Project Files

- Firmware: `firmware/04_dht22_validation/04_dht22_validation.ino`
- Raw data: `data/raw/dht22_day5.csv`
- Setup photograph: `hardware/photos/day5_sensor_setup.jpg`
- Serial Monitor screenshot: `documentation/day5_serial_monitor.png`
- Contextual comparison photograph: `documentation/day5_reference_comparison.jpg`
- Calculation workbook: `documentation/dht22_day5_calculations.xlsx`
- Validation log: `documentation/dht22_validation_log.md`

## 12. Completion Checklist

- [x] ESP32 and DHT22 connected (as reported)
- [x] Serial Monitor screenshot captured (as reported)
- [x] 99 data rows reviewed from supplied output
- [x] Valid and invalid readings counted for supplied output
- [x] Temperature statistics calculated from supplied output
- [x] Humidity statistics calculated from supplied output
- [x] Timestamp intervals checked
- [x] Calculation workbook created from supplied output
- [x] Markdown review completed
- [ ] 100-reading requirement verified or missing reading recovered
- [ ] Actual saved CSV confirmed to match the supplied output
- [ ] Final files copied into the project folders and reviewed

**Status:** Analysis of the supplied output is complete. The 100-reading requirement remains unresolved because the provided data contains 99 rows.
