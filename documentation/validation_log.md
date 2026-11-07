# Day 24: Data Validation Log

## Objective
To validate telemetry data retrieved from InfluxDB using a Python validation script and export the resulting dataset to CSV.

## Project
- **Project:** Karnaphuli Tunnel Structural Health Monitoring (SHM)
- **Day:** 24
- **Database:** InfluxDB OSS
- **Validation Script:** `python/validate_data.py`

## Implementation
A Python script was created to retrieve telemetry data from InfluxDB, inspect missing values and quality flags, validate the available records, and export the result to a CSV file.

The validation workflow was executed using data collected from the laboratory prototype.

## Data Query and Validation Results
- **Rows retrieved:** 116
- **Columns retrieved:** 19
- **Partial records:** 114
- **Degraded records:** 2
- **Records marked `valid`:** 0
- **Missing values:** 0 in all reported columns

## Quality Flag Summary

| Quality Flag | Number of Records |
|---|---:|
| partial | 114 |
| degraded | 2 |
| valid | 0 |
| **Total** | **116** |

## CSV Export
- **Output file:** `python/validated_data.csv`
- **Rows saved:** 116
- **Columns saved:** 19
- **File size:** 24,950 bytes
- **File verification:** Successful

The CSV file was created successfully, and the saved row and column counts were verified.

## Observations
1. The InfluxDB query completed successfully.
2. The retrieved dataset contained no missing values in the reported columns.
3. All 116 records were labelled `partial` or `degraded`; no record had the `valid` quality flag.
4. The available records were preserved in the exported CSV for further inspection.
5. HX711 load-cell calibration remains unverified.
6. The sensor readings were collected using a laboratory prototype and have not been validated against measurements from the actual Karnaphuli Tunnel.

## Limitations
The successful query and CSV export demonstrate that the data retrieval workflow is functioning. However, the dataset has not yet produced fully valid records under the current quality criteria.

The absence of missing values does not, by itself, establish sensor accuracy or measurement validity. Load-cell calibration and the data-quality criteria require further verification.

## Conclusion
Day 24's validation script implementation, data inspection, and CSV export verification were completed. However, full data validation remains incomplete because no records were marked `valid`.

Further work is required to investigate the quality flags and verify load-cell calibration before treating the affected measurements as validated physical measurements.