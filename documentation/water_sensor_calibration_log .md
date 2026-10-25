# Day 9 — Water Sensor Calibration Log

## 1. Objective
To characterize the HW-038 water sensor response at nominal water levels of 0, 2, 5, 8, and 10 cm using 20 ESP32 ADC readings per level.

## 2. Hardware and acquisition
- Board: ESP32
- Sensor: HW-038 water sensor
- Analog input: GPIO34
- Nominal levels: 0, 2, 5, 8, and 10 cm
- Readings recorded: 20 per level; 100 total
- Serial Monitor baud rate: 115200
- AO voltage independently checked with a multimeter: No
- Voltage column: ESP32 `analogReadMilliVolts()` reported estimate, not independently verified voltage

## 3. Data files
- Raw readings and summary statistics: `data/calibration/water_sensor_calibration.xlsx`
- Raw data sheet: `Raw_Data`
- Summary statistics sheet: `Summary`
- Calculation notes: `Calculation_Notes`

## 4. Summary results

| Water level (cm) | N | Mean ADC | Sample SD (ADC) | Mean reported voltage (mV) |
|---:|---:|---:|---:|---:|
| 0 | 20 | 22.80 | 8.26 | 159.95 |
| 2 | 20 | 1893.35 | 7.39 | 1703.50 |
| 5 | 20 | 1991.35 | 5.29 | 1787.30 |
| 8 | 20 | 2011.85 | 4.73 | 1803.25 |
| 10 | 20 | 1902.80 | 97.99 | 1712.45 |

## 4A. Statistical Formulas and Calculation Method

For each nominal water level (0, 2, 5, 8, and 10 cm), 20 readings were collected (`N = 20`). The summary statistics were calculated from the raw readings as follows.

### Sample count

\[N = \text{number of valid readings}\]

Here, `N = 20` for each water level.

### Mean ADC

\[\bar{x} = \frac{1}{N}\sum_{i=1}^{N} x_i\]

where `x_i` is the *i*-th ADC reading and `N` is the number of readings.

### Sample standard deviation of ADC

\[s = \sqrt{\frac{\sum_{i=1}^{N}(x_i-\bar{x})^2}{N-1}}\]

The sample standard deviation (`STDEV.S` in Excel) describes the spread of the ADC readings around their mean.

### Mean reported voltage

\[\bar{V} = \frac{1}{N}\sum_{i=1}^{N} V_i\]

where `V_i` is the voltage value in millivolts reported by ESP32's `analogReadMilliVolts()` for the *i*-th reading.

### Excel formulas

If the 20 ADC values for one water level are in `B2:B21` and their reported voltage values are in `C2:C21`, the corresponding Excel formulas are:

| Statistic | Excel formula |
|---|---|
| N | `=COUNT(B2:B21)` |
| Mean ADC | `=AVERAGE(B2:B21)` |
| Sample SD (ADC) | `=STDEV.S(B2:B21)` |
| Mean reported voltage (mV) | `=AVERAGE(C2:C21)` |

Adjust the cell ranges for each level's 20 raw readings. These are illustrative ranges; use the actual ADC and voltage columns/ranges in the workbook. The reported voltage is an ESP32 ADC-derived estimate and was not independently verified with a multimeter.

## 5. Observations
- ADC readings changed substantially between the dry baseline (0 cm) and the wet levels.
- The mean ADC increased from 2 cm to 8 cm in these measurements.
- The 10 cm readings do not follow the same trend: samples 1–17 are around 1853–1872 ADC, while samples 18–20 are 2124, 2137, and 2128 ADC.
- During the 10 cm test, the water level was not maintained at a constant height during the final three measurements. The corresponding ADC readings were 2124, 2137, and 2128.
- These three readings were retained in the raw dataset and included in the original 10 cm summary statistics; they were not deleted or silently excluded.
- A later repeat measurement was collected separately after the water level was kept constant. Repeat data must remain separate from this Day 9 dataset.

## 5A. 10 cm Water-Level Stability Observation
During the 10 cm calibration test, the water level was not maintained at a constant height during the final three measurements. The corresponding ADC readings were 2124, 2137, and 2128. These readings were retained in the original dataset to preserve the experimental record. They remain included in the Day 9 summary statistics and are flagged as affected by the observed water-level instability. Repeat measurements collected later are stored separately and do not overwrite the original data.

## 6. Limitations
- AO voltage was not independently verified using a multimeter; reported millivolts are ADC-derived estimates.
- The calibration is preliminary and should not be described as a validated depth measurement.
- Water conductivity, sensor placement, and immersion geometry can affect a resistive water sensor.
- To assess repeatability, inspect the setup and repeat the 10 cm measurement if possible, preserving the original data and recording the repeat separately.

## 7. Evidence photographs
Five level photographs were saved in `hardware/photos/` with the following filenames:
- 0 cm: `hardware/photos/day9_01_dry_0cm.jpg`
- 2 cm: `hardware/photos/day9_02_level_2cm.jpg`
- 5 cm: `hardware/photos/day9_03_level_5cm.jpg`
- 8 cm: `hardware/photos/day9_04_level_8cm.jpg`
- 10 cm: `hardware/photos/day9_05_level_10cm.jpg`

## 8. Status
100 original readings have been recorded and summarized. The water-level instability observed during the final three 10 cm measurements is documented. Independent AO voltage verification with a multimeter remains pending.
