# Day 11: Load Cell and HX711 Calibration Log

## 1. Objective
To calibrate a 5 kg load cell connected to an ESP32 through an HX711 amplifier and evaluate its measurement stability using a known 100 g weight.

## 2. Hardware and Wiring
- ESP32 DOIT DEVKIT V1
- 5 kg bar-type load cell
- HX711 amplifier module
- HX711 DOUT/DT → ESP32 GPIO 18
- HX711 SCK → ESP32 GPIO 19
- Power and ground connected to the module as used during testing

## 3. Tests Performed
- Checked whether the HX711 was responding.
- Performed tare with the platform empty.
- Observed raw ADC and net raw readings.
- Attempted calibration using a known 100 g weight.
- Attempted repeated validation measurements.

## 4. Calibration and Validation Results

### Attempt A: Calibration factor = -5921.79
Calibration check with 100 g: approximately 100.01 g.

| Trial | Known weight | Measured weight | Absolute error | Error (%) |
|---|---:|---:|---:|---:|
| 1 | 100 g | 100.02 g | 0.02 g | 0.02% |
| 2 | 100 g | 99.89 g | 0.11 g | 0.11% |
| 3 | 100 g | 92.17 g | 7.83 g | 7.83% |

### Attempt B: Calibration factor = 187.0
Calibration check with 100 g: approximately 100.07 g.

| Trial | Known weight | Measured weight | Absolute error | Error (%) |
|---|---:|---:|---:|---:|
| 1 | 100 g | 50.72 g | 49.28 g | 49.28% |
| 2 | 100 g | 50.70 g | 49.30 g | 49.30% |
| 3 | 100 g | 50.24 g | 49.76 g | 49.76% |

### Attempt C: Calibration factor = -8.5
Calibration net raw reading: -850. The calibration check did not match the known 100 g weight.

| Trial | Known weight | Measured weight | Absolute error | Error (%) |
|---|---:|---:|---:|---:|
| 1 | 100 g | 21.88 g | 78.12 g | 78.12% |
| 2 | 100 g | 35.18 g | 64.82 g | 64.82% |
| 3 | 100 g | -29.41 g | 129.41 g | 129.41% |

*Note: These are separate calibration attempts. The factors and readings must not be treated as one successful calibration run.*

## 5. Empty-Platform Diagnostic
During one diagnostic run, the empty-platform net raw readings fluctuated around zero, with observed values ranging approximately from -176 to 62 counts. This indicates that tare was able to bring readings near zero in that run, but it does not establish accurate weight measurement under load.

## 6. Problems Observed
- The measured weight was inconsistent across calibration attempts.
- Some validation readings were substantially different from the known 100 g weight.
- In one attempt, the calibration check appeared close to 100 g, but the subsequent validation readings were around 50 g.
- The calibration factor differed between attempts.
- The cause of the inconsistent readings has not yet been confirmed.

## 7. Conclusion
A preliminary 100 g calibration and validation experiment was attempted. However, measurement stability and repeatability could not be confirmed. Therefore, the load cell calibration is **not yet validated**, and the results should not be reported as a successful calibration.

Further troubleshooting of the mechanical mounting, wiring, tare procedure, and calibration code is required before repeating validation. The results recorded here are preliminary experimental observations.

## 8. Files
- Calibration spreadsheet: `data/calibration/loadcell_calibration.xlsx`
- This log: `documentation/loadcell_calibration_log.md`
