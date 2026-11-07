# Day 25: Calibration Calculation Log

## Objective
To process water sensor and load cell calibration data using Python and calculate statistical measurements for calibration analysis.

## Project Information
- Project: Karnaphuli Tunnel Structural Health Monitoring (SHM)
- Day: 25
- Programming Language: Python
- Libraries: Pandas, NumPy, OpenPyXL

## 1. Python Calibration Script

- Script: `python/calculate_calibration.py`
- Implemented `calculate_calibration()` function.
- Calculated Mean ADC.
- Calculated Standard Deviation.
- Processed existing Excel calibration datasets.

## 2. Water Sensor Calibration

- Sensor: HW-038
- Input: `data/calibration/water_sensor_calibration.xlsx`
- Source Sheet: `Raw_Data`
- Water levels: 0, 2, 5, 8, 10 cm
- Total readings: 100

### Statistical Results

| Water Level (cm) | Samples | Mean ADC | STD |
|---:|---:|---:|---:|
| 0 | 20 | 22.80 | 8.26 |
| 2 | 20 | 1893.35 | 7.39 |
| 5 | 20 | 1991.35 | 5.29 |
| 8 | 20 | 2011.85 | 4.73 |
| 10 | 20 | 1902.80 | 97.99 |

### Observation

The sensor showed relatively stable readings at 2, 5, and 8 cm. However, higher variability and a decrease in mean ADC were observed at 10 cm.

### Output

`data/calibration/water_sensor_calibration.xlsx`

New Sheet: `Day25_Water_Summary`

## 3. Load Cell Calibration

- Sensor: Load Cell + HX711
- Input: `data/calibration/loadcell_calibration.xlsx`
- Source Sheet: `Sheet1`
- Calibration attempts: A, B, C
- Total measured trials: 9
- Known weight: 100 g

### Statistical Results

| Attempt | Mean Weight (g) | STD (g) | Mean Error (%) |
|---|---:|---:|---:|
| A | 97.36 | 4.50 | 2.65 |
| B | 50.55 | 0.27 | 49.45 |
| C | 9.22 | 34.11 | 90.78 |

### Observation

Attempt A showed the closest average measurement to the known 100 g reference weight. Attempt B showed consistent but inaccurate measurements, while Attempt C showed substantial instability.

The load cell calibration is not yet considered reliable or fully validated.

### Output

`data/calibration/loadcell_calibration.xlsx`

New Sheet: `Day25_LoadCell_Summary`

## 4. Limitations

- Load cell raw ADC measurements were not available in the existing calibration workbook.
- Load cell analysis was therefore performed using measured weight and error values.
- Further mechanical mounting, calibration, and independent validation experiments are required.

## 5. Conclusion

Python-based statistical processing of water sensor and load cell calibration datasets was successfully completed.

Mean values, standard deviations, sample counts, minimum values, maximum values, and measurement errors were calculated where applicable.

The resulting statistical summaries were saved in the existing Excel workbooks for further analysis in the Karnaphuli Tunnel SHM project.