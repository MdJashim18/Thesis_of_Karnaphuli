# Day 14: Week 2 Acceptance Test Report

## 1. Objective
To evaluate the ESP32-based combined sensor monitoring prototype through a 30-minute continuous data-collection run and individual sensor response tests.

## 2. Test Setup
- Device ID: `ESP32-GW-LAB-001`
- Zone ID: `LAB_PROTOTYPE`
- Firmware: `firmware/08_all_sensors/08_all_sensors.ino`
- Serial baud rate: 115200
- Data file analyzed: `data/raw/week2_test.jsonl`
- Sampling interval configured: 2 seconds

## 3. Test Results

### Test 1: 30-Minute Continuous Run
The supplied JSONL file was programmatically checked.

- Number of records: 900
- First timestamp: 2,000 ms
- Last timestamp: 1,800,000 ms
- Elapsed time between first and last records: 1,798 seconds (29 minutes 58 seconds)
- Observed intervals: 899 intervals of 2,000 ms each
- Invalid JSON lines: 0
- Unexpected reset/interruption: Not determinable from this file alone
- Result: The file contains approximately 30 minutes of consistently spaced records. A full pass decision also depends on whether any reset or interruption was observed during the run.

### Test 2: DHT22 Sensor Disconnect
- Test performed: Yes, according to the user's test log/confirmation.
- Wiring safety: ESP32 power was turned off before changing wiring.
- Exact readings during disconnection and after reconnection: Not available in the supplied 30-minute JSONL file.
- Result: Test performed; the response cannot be independently verified from this file alone.

### Test 3: Water Sensor Dry/Wet Response
- Test performed: Yes, according to the user's test log/confirmation.
- In the supplied 30-minute dataset, `water_raw` was 0 in all 900 records.
- Separate dry-state and wet-state test readings: Not included in this file.
- Result: The continuous-run data alone does not demonstrate a dry/wet response. Use the separate test observations to document this test.

### Test 4: Load Cell Response
- Test performed: Yes, according to the user's test log/confirmation.
- Numeric `load_raw` readings: 898 records
- `load_raw` missing/null: 2 records
- Observed `load_raw` range in this dataset: -53,203 to -45,239
- `load_kg`: null in all 900 records
- Weight calibration: Not verified
- Result: Raw readings were collected, but calibrated weight values and repeatability are not validated.

### Test 5: MPU6050 Tap Response
- Test performed: Yes, according to the user's test log/confirmation.
- Acceleration and gyroscope readings are present in all 900 continuous-run records.
- Separate baseline, tap, and recovery readings: Not identified in the supplied file.
- Result: The continuous-run data confirms that MPU6050 values were recorded, but the tap response cannot be independently evaluated without the corresponding test observations.

### Test 6: DHT22 Environmental Response
- Test performed: Yes, according to the user's test log/confirmation.
- Temperature range in the supplied continuous-run dataset: 33.4–34.2 °C
- Humidity range in the supplied continuous-run dataset: 82.8–86.4%
- Separate readings before and after the environmental change: Not identified in the supplied file.
- Result: DHT22 readings were recorded throughout the run; the specific environmental-response test needs its separate observations for confirmation.

## 4. Data Quality
- JSONL file exists and was readable: Yes
- Total records: 900
- Valid JSON records: 900
- Invalid JSON lines: 0
- `quality_flag`: `partial` in all 900 records
- Missing/null `load_raw`: 2 records
- Missing/null `load_kg`: 900 records
- Missing/null readings for temperature, humidity, MPU6050 axes, and `water_raw`: 0 records each

## 5. Limitations and Follow-up
1. Load-cell calibration and repeatability remain unverified. Do not treat `load_kg` as a valid weight measurement.
2. `water_raw` remained 0 throughout this continuous-run dataset. The separate dry/wet test observations are needed to assess the sensor response.
3. All records have `quality_flag: partial`. The current firmware's validation condition requires a verified load-cell calibration, so this flag is expected while `LOAD_CELL_CALIBRATED` remains `false`.
4. The JSONL file does not by itself identify the exact start/end times or readings for the separate disconnect, water, tap, and environmental-response tests.
5. No reset/interruption status can be concluded from the JSONL records alone.

## 6. Conclusion
The 30-minute continuous data collection produced 900 valid JSONL records at regular 2-second intervals, spanning 29 minutes 58 seconds between the first and last timestamps. Temperature, humidity, MPU6050, and water-sensor fields were present in all records. The water ADC value remained 0 in this run, `load_raw` was missing in two records, `load_kg` was null throughout, and every record was marked `partial`.

The user reports that the individual sensor response tests were also performed. Their detailed results should be added from the notes or Serial Monitor observations before marking those tests as passed. Load-cell and water-sensor calibration remain outstanding.

## 7. Output Files
- `documentation/week2_acceptance_test.md`
- `data/raw/week2_test.jsonl`
