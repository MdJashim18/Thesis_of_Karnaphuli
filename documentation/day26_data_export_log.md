# Day 26: InfluxDB Data Export Log

## 1. Objective

To develop a Python data export script to retrieve telemetry data from InfluxDB and export it into a CSV file for further data analysis and machine learning preparation.

## 2. Project Information

- **Project:** Karnaphuli Tunnel Structural Health Monitoring (SHM)
- **Day:** 26
- **Database:** InfluxDB OSS
- **Bucket:** `tunnel_telemetry`
- **Programming Language:** Python
- **Export Script:** `python/export_data.py`
- **Output Directory:** `data/cleaned/`

## 3. Software and Libraries

The following Python libraries were used:

- `pandas`
- `influxdb-client`
- `InfluxDBClient`

## 4. Implementation

A Python script named `export_data.py` was created inside the `python/` directory.

The script connects to InfluxDB using the configuration values stored in `python/config.py`.

The following Flux query was used to retrieve telemetry data from the last one hour:

```flux
from(bucket: "tunnel_telemetry")
  |> range(start: -1h)
```

The retrieved data was converted into a Pandas DataFrame and exported as a CSV file.

## 5. Execution

The script was executed from the project root directory using:

```bash
python python/export_data.py
```

The script connected to InfluxDB, retrieved telemetry records, and successfully generated the CSV file.

## 6. Export Results

| Parameter | Result |
|---|---|
| Export Status | Successful |
| Bucket | `tunnel_telemetry` |
| Time Range | Last 1 hour |
| Total Records | 2,101 |
| Total Columns | 12 |
| Output Format | CSV |

## 7. Exported Columns

The exported CSV file contains the following 12 columns:

1. `result`
2. `table`
3. `_start`
4. `_stop`
5. `_time`
6. `_value`
7. `_field`
8. `_measurement`
9. `device_id`
10. `gateway_id`
11. `quality_flag`
12. `zone_id`

## 8. Output File

The exported dataset was saved at:

```text
data/cleaned/month2_final_dataset.csv
```

## 9. Warning and Observation

During execution, InfluxDB displayed a `MissingPivotFunction` warning because the Flux query did not include a `pivot()` function.

This warning did not interrupt the export process.

The CSV file was generated successfully with 2,101 records and 12 columns.

The exported dataset is currently in long format, where sensor field names and their corresponding values are stored in separate rows.

## 10. Limitations

- The current query retrieves only the last one hour of telemetry data.
- The export does not represent the complete historical dataset.
- The data has not yet been converted into a pivoted wide-format structure.

## 11. Conclusion

The Day 26 data export task was successfully completed.

A Python script was developed to retrieve telemetry data from the InfluxDB `tunnel_telemetry` bucket and export it into CSV format.

The resulting dataset contains 2,101 records and 12 columns and is available for subsequent data processing, validation, visualization, and machine learning preparation.