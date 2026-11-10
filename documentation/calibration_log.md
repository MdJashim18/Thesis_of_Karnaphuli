# Sensor Calibration and Validation Log
## Karnaphuli Tunnel Real-Time Structural Health Monitoring Prototype

**Date:** 09 November 2026  
**Sensor:** Load Cell + HX711  
**Microcontroller:** ESP32  
**Device ID:** ESP32-GW-LAB-001

---

## 1. Calibration Objective

The objective of this experiment is to calibrate the load cell
connected to the HX711 amplifier and evaluate its measurement
accuracy using known reference weights.

The calibration process includes:

1. Empty-platform tare.
2. Reference-weight measurement.
3. Calibration factor calculation.
4. Multi-weight validation.
5. Repeated measurements.
6. Error analysis.

---

## 2. Calibration Procedure

### Step 1: Tare

The load cell platform was kept empty.

The HX711 average raw reading was recorded as the offset.

The tare process establishes the baseline measurement.

### Step 2: Calibration

A known 100 g reference weight was used during the earlier
validation experiment.

Calibration factor:

402.619995

The calibration check reported:

- Calibration weight: 100.00 g
- Measured check: 99.76 g

### Step 3: Multi-Weight Validation

Four reference weights were used:

- 100 g
- 200 g
- 500 g
- 1000 g

Each weight was measured three times.

The platform was emptied and tared before each trial.

---

## 3. Multi-Weight Validation Results

### 3.1 Validation Summary

| Reference Weight | Mean Measured | Mean Error | Mean Absolute Error |
|---|---:|---:|---:|
| 100 g | 99.363 g | -0.637 g | 0.637% |
| 200 g | 200.249 g | +0.249 g | 0.184% |
| 500 g | 501.252 g | +1.252 g | 0.250% |
| 1000 g | 861.954 g | -138.046 g | 13.805% |

### 3.2 Detailed Validation Results

#### 100 g

| Trial | Measured (g) | Error (g) | Absolute Error (%) |
|---|---:|---:|---:|
| 1 | 99.354 | -0.646 | 0.646 |
| 2 | 99.225 | -0.775 | 0.775 |
| 3 | 99.508 | -0.492 | 0.492 |

Mean measured: 99.363 g  
Standard deviation: 0.142 g  
Mean absolute percentage error: 0.637%

#### 200 g

| Trial | Measured (g) | Error (g) | Absolute Error (%) |
|---|---:|---:|---:|
| 1 | 200.842 | +0.842 | 0.421 |
| 2 | 200.084 | +0.084 | 0.042 |
| 3 | 199.821 | -0.179 | 0.089 |

Mean measured: 200.249 g  
Standard deviation: 0.530 g  
Mean absolute percentage error: 0.184%

#### 500 g

| Trial | Measured (g) | Error (g) | Absolute Error (%) |
|---|---:|---:|---:|
| 1 | 500.951 | +0.951 | 0.190 |
| 2 | 501.808 | +1.808 | 0.362 |
| 3 | 500.996 | +0.996 | 0.199 |

Mean measured: 501.252 g  
Standard deviation: 0.482 g  
Mean absolute percentage error: 0.250%

#### 1000 g

| Trial | Measured (g) | Error (g) | Absolute Error (%) |
|---|---:|---:|---:|
| 1 | 866.594 | -133.406 | 13.341 |
| 2 | 861.254 | -138.746 | 13.875 |
| 3 | 858.015 | -141.985 | 14.198 |

Mean measured: 861.954 g  
Standard deviation: 4.332 g  
Mean absolute percentage error: 13.805%

---

## 4. Current ESP32 Calibration Status

The latest ESP32 firmware calibration status was:

Offset: -610958  
Scale: 403550.000 raw/kg  
Tare: COMPLETED  
Calibration: ACTIVE

The current firmware stores:

- Offset
- Scale factor
- Tare completion status
- Calibration activation status

The current calibration factor is approximately equivalent
to 403.55 raw/g.

This is a separate firmware calibration record from the
earlier validation script factor of 402.619995.

Both records should be preserved separately.

---

## 5. InfluxDB Load Cell Verification

The latest InfluxDB Data Explorer screenshot shows:

| Parameter | Observed Value |
|---|---:|
| load_kg | 0.20381 |
| load_raw | -528712 |
| quality_flag | ok |

The displayed load value demonstrates that the ESP32 firmware
is calculating a non-zero load measurement and transmitting it
to the backend.

The raw reading is negative because the HX711 output polarity
and tare reference determine the sign of the raw count.

A negative raw count does not automatically indicate a
measurement failure.

---

## 6. Calibration Analysis

The validation results indicate:

- Good measurement performance at 100 g.
- Good measurement performance at 200 g.
- Good measurement performance at 500 g.
- Significant underestimation at 1000 g.

The 1000 g result indicates a possible load-dependent
measurement error.

Potential causes include:

1. Mechanical mounting or load distribution.
2. Load cell capacity or non-linearity.
3. Platform friction or contact with surrounding objects.
4. Reference weight uncertainty.
5. Wiring or electrical noise.
6. Calibration factor limitations.
7. Mechanical deformation or overload.

The current evidence does not establish the exact cause.

---

## 7. Recommended Additional Calibration Work

Before using the sensor for quantitative structural load
measurement, the following tests are recommended:

- Repeat the 1000 g test after inspecting the mechanical setup.
- Test additional weights between 500 g and 1000 g.
- Check whether the load is applied at the center.
- Inspect the load cell mounting and HX711 wiring.
- Repeat tests with multiple load positions.
- Compare measurements against a verified reference scale.
- Perform a separate calibration verification using the
  current firmware calibration factor.

---

## 8. Conclusion

The load cell calibration and validation process was completed.

The sensor demonstrated low measurement error for 100 g,
200 g, and 500 g reference weights.

However, the 1000 g validation results showed approximately
13.805% mean absolute error.

Therefore, the load cell is suitable for continued prototype
testing within the validated lower measurement range, while
additional investigation is required before claiming accurate
measurement at 1000 g.

Calibration accuracy should not be generalized beyond the
tested range.