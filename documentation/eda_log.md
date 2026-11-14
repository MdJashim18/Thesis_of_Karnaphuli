# Month 3 – Day 1: Exploratory Data Analysis (EDA)

**Project:** Karnaphuli Tunnel Structural Health Monitoring (SHM)  
**Activity:** Initial Exploratory Data Analysis  
**Dataset:** `month2_final_dataset.csv`  
**Analysis Notebook:** `notebooks/01_eda.ipynb`  
**Date:** 14 November 2026  
**Status:** Completed

---

## 1. Objective

The primary objective of Day 1 was to perform an initial Exploratory Data Analysis (EDA) on the telemetry dataset collected during Month 2 of the Karnaphuli Tunnel SHM prototype.

The analysis focuses on:

- Understanding the structure and characteristics of the collected dataset.
- Examining descriptive statistics of sensor measurements.
- Identifying missing values and duplicate records.
- Evaluating sensor validity and data quality.
- Investigating numerical outliers.
- Reviewing load cell calibration and validation evidence.
- Identifying timestamp and latency anomalies for further investigation.
- Preparing analysis reports for subsequent data preprocessing and model development.

## 2. Dataset Information

The dataset was collected through the ESP32-based SHM prototype and exported from the Month 2 data collection process.

**Dataset location:**

`data/raw/month2_final_dataset.csv`

| Attribute | Value |
|---|---|
| Total records | 3,483 |
| Total columns | 30 |
| File format | CSV |
| Data source | ESP32-based SHM prototype |
| Primary device ID | ESP32-GW-LAB-001 |
| Gateway ID | gateway01 |
| Zone ID | LAB_PROTOTYPE |
| Timestamp field | received_at |

The dataset contains environmental, vibration, water-related and load-related measurements, together with device metadata, timestamps, calibration information and data-quality indicators.

### 2.1 Sensor Features

The principal sensor-related fields include:

- `temperature`
- `humidity`
- `accel_x`
- `accel_y`
- `accel_z`
- `water_raw`
- `load_raw`
- `load_kg`
- `load_gram`

Additional metadata and validation fields include:

- `device_id`
- `gateway_id`
- `zone_id`
- `boot_id`
- `sequence_number`
- `quality_flag`
- `dht_valid`
- `mpu_valid`
- `hx711_valid`
- `latency_valid`
- `device_timestamp_valid`
- `latency_audit_valid`
- `load_calibrated`

## 3. Dataset Loading and Inspection

The dataset was loaded using Python Pandas.

The following initial inspection operations were performed:

- Dataset shape inspection.
- Column name inspection.
- Data type inspection.
- First and last record inspection.
- Descriptive statistical analysis.

The dataset was successfully loaded with:

- 3,483 rows.
- 30 columns.

The `received_at` column was used as the primary received timestamp and converted into a datetime representation where applicable.

## 4. Descriptive Statistical Analysis

Descriptive statistics were generated for the numerical and categorical fields.

### 4.1 Selected Sensor Statistics

| Sensor | Mean | Minimum | Maximum |
|---|---:|---:|---:|
| Temperature (°C) | 28.6195 | 26.3 | 32.6 |
| Humidity (%) | 80.3900 | 72.3 | 90.9 |
| Accel X | 0.1795 | 0.069 | 0.402 |
| Accel Y | 0.0200 | -0.108 | 0.151 |
| Accel Z | 10.9564 | 10.623 | 11.265 |
| Water raw | 23.3597 | 0 | 1485 |
| Load (kg) | 0.06161 | 0 | 0.20973 |

**Observation:**

The temperature and humidity readings show measurable variation across the collected records. The accelerometer readings also exhibit variation that requires further investigation in the context of vibration monitoring.

The water sensor contains a large number of zero readings, with a smaller number of nonzero readings. This behavior should be considered when designing preprocessing and threshold-based analysis.

The load-related measurements must be interpreted alongside their calibration status and validation results.

### 4.2 Important Data Quality Observation

The `latency_ms` and `device_timestamp_ms` fields contain suspiciously large and negative values.

The observed `latency_ms` statistics include:

- Mean: approximately 44,805,101,239.54 ms.
- Minimum: approximately -1,371.606 ms.
- Maximum: approximately 1,793,813,150,325.627 ms.

These values indicate timestamp or latency calculation anomalies.

They must not be interpreted as normal network latency measurements. A dedicated timestamp and latency audit is required before using these fields for communication-performance evaluation.

## 5. Missing Value Analysis

Missing values were identified using Pandas.

**Total missing cells:** 6,110.

| Column | Missing Values | Missing Percentage |
|---|---:|---:|
| `boot_id` | 3,198 | 91.82% |
| `load_calibrated` | 1,456 | 41.80% |
| `load_gram` | 1,456 | 41.80% |
| Other columns | 0 | 0% |

**Observation:**

Most missing values are concentrated in device boot metadata and load cell calibration-related fields.

The missing `boot_id` values should be investigated as a metadata completeness issue.

The missing `load_gram` and `load_calibrated` values indicate that calibrated load measurements are not available for every record.

Missing values should not automatically be replaced with zero because zero may represent a genuine sensor reading.

## 6. Duplicate Record Analysis

Duplicate records were checked using Pandas.

| Metric | Result |
|---|---:|
| Total records | 3,483 |
| Duplicate records | 0 |
| Unique records | 3,483 |

**Observation:**

No exact duplicate records were identified in the dataset.

This indicates that the exported dataset does not contain exact row-level duplicates. However, this does not independently establish that every sensor reading is temporally unique.

## 7. Data Quality Analysis

The distribution of the `quality_flag` field was examined.

| Quality Flag | Records | Percentage |
|---|---:|---:|
| partial | 2,412 | 69.25% |
| ok | 1,068 | 30.66% |
| degraded | 3 | 0.09% |
| **Total** | **3,483** | **100%** |

**Observation:**

Most records are classified as `partial`, while approximately 30.66% are classified as `ok`.

The quality flag should be considered during subsequent preprocessing and analysis.

A `partial` record should not automatically be discarded. Its individual sensor validity flags and available measurements should be examined before deciding whether it can be used.

## 8. Sensor Validity Analysis

The sensor validity indicators were examined to understand the availability and reliability of measurements.

### 8.1 Validity Results

| Field | Status | Records |
|---|---|---:|
| `dht_valid` | True | 3,483 |
| `mpu_valid` | True | 3,483 |
| `hx711_valid` | True | 3,480 |
| `hx711_valid` | False | 3 |
| `latency_valid` | True | 1,729 |
| `latency_valid` | False | 1,754 |
| `device_timestamp_valid` | True | 3,396 |
| `device_timestamp_valid` | False | 87 |
| `latency_audit_valid` | True | 1,729 |
| `latency_audit_valid` | False | 1,754 |
| `load_calibrated` | True | 1,068 |
| `load_calibrated` | False | 959 |
| `load_calibrated` | Missing | 1,456 |

**Observation:**

The DHT and MPU validity flags are true for all records.

Three records have an invalid HX711 validity flag.

A considerable number of records have invalid latency and timestamp audit indicators. These fields require further investigation before communication-performance analysis.

Load cell calibration availability is also incomplete across the dataset.

## 9. Outlier Analysis

The Interquartile Range (IQR) method was applied to selected numerical sensor measurements.

The following formula was used:

\[
IQR = Q3-Q1
\]

\[
Lower=Q1-1.5(IQR)
\]

\[
Upper=Q3+1.5(IQR)
\]

### 9.1 Outlier Detection Results

| Feature | Q1 | Q3 | IQR Outliers |
|---|---:|---:|---:|
| Temperature | 27.2 | 29.7 | 0 |
| Humidity | 76.7 | 83.3 | 0 |
| Accel X | 0.156 | 0.204 | 19 |
| Accel Y | 0.000 | 0.041 | 44 |
| Accel Z | 10.903 | 11.011 | 7 |
| Water raw | 0 | 0 | 107 |
| Load (kg) | 0 | 0.204 | 0 |
| Load (gram) | 0 | 205.985 | 0 |

### 9.2 Interpretation

The IQR method identified a small number of potential outliers in the accelerometer measurements.

No IQR outliers were identified in temperature, humidity, load in kilograms or load in grams.

**Important water sensor observation:**

The first and third quartiles of `water_raw` are both zero. Therefore, the IQR is also zero, and the IQR method identifies all nonzero readings as outliers.

This does not establish that these readings are erroneous. Nonzero values may represent genuine water sensor responses.

Therefore, water sensor readings must be investigated using their calibration behavior and physical operating conditions rather than being automatically removed.

**Outlier handling decision:**

No outliers were automatically removed during Day 1. The identified values will be retained for further investigation.

## 10. Load Cell Calibration and Validation Analysis

The load cell and HX711 module were calibrated and validated during Month 2.

The calibration evidence was reviewed as part of the Day 1 EDA.

### 10.1 Calibration Procedure

The calibration procedure included:

1. Empty-platform tare.
2. Calibration using a reference weight.
3. Measurement using multiple reference weights.
4. Three measurement trials for each reference weight.
5. Calculation of mean measurement error and standard deviation.

The multi-weight validation was conducted on 9 November 2026.

### 10.2 Multi-Weight Validation Results

| Reference Weight | Mean Measured Weight | Standard Deviation | MAPE |
|---|---:|---:|---:|
| 100 g | 99.363 g | 0.142 g | 0.637% |
| 200 g | 200.249 g | 0.530 g | 0.184% |
| 500 g | 501.252 g | 0.482 g | 0.250% |
| 1,000 g | 861.954 g | 4.332 g | 13.805% |

Mean Absolute Percentage Error (MAPE) was calculated as:

\[
MAPE=\frac{|Measured-Reference|}{Reference}\times100
\]

### 10.3 Calibration Metadata

The calibration records include:

| Parameter | Recorded Value |
|---|---:|
| Device ID | ESP32-GW-LAB-001 |
| Earlier validation script factor | 402.619995 |
| Later firmware offset | -610958 |
| Later firmware scale | 403550 raw/kg |
| Equivalent firmware scale | Approximately 403.55 raw/g |
| Calibration status | Active in later firmware record |

The earlier validation script factor and later firmware scale are separate records from different calibration stages. They should not be treated as interchangeable values.

### 10.4 Calibration Interpretation

The load cell demonstrated good measurement agreement at 100 g, 200 g and 500 g reference weights.

However, the 1,000 g validation result showed significant underestimation, with a MAPE of approximately 13.805%.

Possible contributing factors include mechanical mounting, load distribution, sensor nonlinearity, reference-weight accuracy, wiring and measurement noise. These are potential explanations, not confirmed causes.

Further investigation should include:

- Repeating the 1,000 g validation.
- Inspecting the load cell mounting arrangement.
- Checking the mechanical load distribution.
- Testing intermediate weights between 500 g and 1,000 g.
- Verifying the reference weights and current firmware calibration settings.

**Conclusion:**

The load cell appears suitable for prototype testing within the validated lower measurement range. Its accuracy at 1,000 g has not been established and requires further validation.

## 11. Timestamp and Latency Anomaly Investigation

The initial descriptive analysis identified suspicious values in:

- `device_timestamp_ms`
- `latency_ms`
- `latency_valid`
- `device_timestamp_valid`
- `latency_audit_valid`

The presence of negative and extremely large latency values suggests that timestamp consistency and latency calculation require additional investigation.

The following tasks are planned for a subsequent analysis stage:

1. Verify the device timestamp format.
2. Check timestamp units and conversion.
3. Compare device timestamps with server-side `received_at`.
4. Identify invalid and inconsistent timestamp records.
5. Recalculate latency using a consistent timestamp basis.
6. Evaluate missing records and communication delays.

These anomalies should be addressed before reporting reliable network latency statistics.

## 12. Initial EDA Findings

The Day 1 analysis identified the following findings:

1. The Month 2 dataset contains 3,483 records and 30 columns.
2. No exact duplicate records were identified.
3. Missing values are concentrated in `boot_id`, `load_calibrated` and `load_gram`.
4. Approximately 69.25% of records have a `partial` quality flag.
5. DHT and MPU validity indicators are true for all records.
6. A small number of accelerometer readings were flagged by the IQR method.
7. Nonzero water sensor readings require physical interpretation rather than automatic removal.
8. Load cell validation showed good agreement at 100 g, 200 g and 500 g, but significant error at 1,000 g.
9. Timestamp and latency fields contain anomalies requiring a dedicated audit.

## 13. Data Handling Decisions

The following decisions were made based on the initial EDA:

- Preserve the original raw dataset.
- Do not automatically remove IQR-detected outliers.
- Do not replace all missing values with zero.
- Investigate incomplete device metadata.
- Consider sensor validity and quality flags during preprocessing.
- Preserve calibration evidence from Month 2.
- Investigate timestamp and latency anomalies separately.
- Avoid making unsupported claims about sensor accuracy outside the validated calibration range.

## 14. Generated EDA Reports

The following report files were generated successfully and saved in the `outputs/` directory.

| File | Description |
|---|---|
| `descriptive_statistics.csv` | Descriptive statistics of the dataset |
| `missing_value_report.csv` | Missing value analysis |
| `quality_report.csv` | Quality flag distribution |
| `sensor_validity_report.csv` | Sensor validity summary |
| `load_cell_calibration_validation.csv` | Multi-weight load cell validation results |
| `calibration_metadata_check.csv` | Calibration metadata consistency |
| `outlier_report.csv` | IQR-based outlier analysis |

The analysis notebook is stored at:

`notebooks/01_eda.ipynb`

## 15. Conclusion

The initial Exploratory Data Analysis of the Month 2 Karnaphuli Tunnel SHM dataset has been completed successfully.

The dataset contains environmental, vibration, water-related and load-related measurements, together with device metadata and quality indicators.

The analysis established an initial understanding of the dataset structure, missing values, data quality, sensor validity, outlier behavior and load cell calibration performance.

Several issues were identified, particularly incomplete metadata, partial-quality records, load cell accuracy at higher reference weights and timestamp/latency inconsistencies.

These findings provide a foundation for the next stage of Month 3, which will focus on data quality assessment, preprocessing and preparation of a reliable dataset for subsequent SHM analysis.

**Day 1 Status: COMPLETED**

---

## 16. Project Directory References

All Month 3 work is maintained inside the existing project directory:

`D:\karnaphuli-shm-month2`

Relevant directories:

```text
karnaphuli-shm-month2/
│
├── data/
│   ├── raw/
│   │   └── month2_final_dataset.csv
│   ├── cleaned/
│   └── processed/
│
├── notebooks/
│   └── 01_eda.ipynb
│
├── src/
│   └── data_loader.py
│
├── documentation/
│   └── eda_log.md
│
├── outputs/
│   ├── descriptive_statistics.csv
│   ├── missing_value_report.csv
│   ├── quality_report.csv
│   ├── sensor_validity_report.csv
│   ├── load_cell_calibration_validation.csv
│   ├── calibration_metadata_check.csv
│   └── outlier_report.csv
│
└── venv/
```

**Documentation file:** `documentation/eda_log.md`  
**Analysis notebook:** `notebooks/01_eda.ipynb`  
**EDA status:** Completed