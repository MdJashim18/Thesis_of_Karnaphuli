# Day 12: Combined Sensor Wiring Log

## 1. Objective

To integrate the DHT22 temperature and humidity sensor, MPU6050 accelerometer and gyroscope, HW-038 analog water sensor, and 5 kg load cell with the ESP32 for the **Karnaphuli Underwater Road Tunnel Structural Health Monitoring (SHM) prototype**.

The objective was to verify preliminary sensor communication, observe readings from the combined setup, identify potential wiring or measurement issues, and document the remaining validation tasks.

## 2. Hardware Components

- ESP32 DOIT DEVKIT V1
- DHT22 temperature and humidity sensor
- MPU6050 accelerometer and gyroscope
- HW-038 analog water sensor
- 5 kg bar-type load cell
- HX711 load-cell amplifier module
- Breadboard and jumper wires
- Digital multimeter

## 3. Pin Connections

| Component | Signal | ESP32 Pin |
|---|---|---|
| DHT22 | DATA | GPIO 4 |
| MPU6050 | SDA | GPIO 21 |
| MPU6050 | SCL | GPIO 22 |
| HW-038 water sensor | AO | GPIO 34 |
| HX711 | DT/DOUT | GPIO 18 |
| HX711 | SCK/CLK | GPIO 19 |

### Communication Interfaces

- DHT22: Digital data interface
- MPU6050: I2C interface
- HW-038: Analog input through GPIO 34
- HX711: Digital interface using DT/DOUT and SCK/CLK

## 4. Power Distribution

| Component | Intended Supply | Verification Status |
|---|---|---|
| DHT22 | 3.3 V, subject to module specifications | Previously operated in individual and combined tests |
| MPU6050 | 3.3 V, subject to module specifications | Previously operated in individual and combined tests |
| HW-038 water sensor | 3.3 V used during testing | Dry/wet response observed |
| HX711 module | Actual supply voltage to be recorded | Not yet verified in this log |
| ESP32 and sensor modules | Common ground | Physical continuity verification not yet documented |

**HX711 supply voltage:** Not yet verified.

**HX711 DOUT logic-level compatibility with ESP32:** Not yet verified.

**Electrical safety note:** ESP32 GPIOs are not 5 V-tolerant. Before final operation, verify that the HX711 DOUT signal remains within the ESP32's permitted input voltage. Do not assume that a module's supply voltage guarantees a safe output logic level.

## 5. Short-Circuit and Continuity Check

The following checklist must be completed based on actual measurements.

| Check | Status | Notes |
|---|---|---|
| All power disconnected before continuity testing | Not yet documented | Record the actual result |
| 3.3 V rail connection verified | Not yet verified | Check the physical connections |
| GND rail connection verified | Not yet verified | Check the physical connections |
| No persistent short between 3.3 V and GND detected | Not yet verified | Check with power disconnected |
| Common ground between ESP32 and modules verified | Not yet verified | Record the actual result |
| HX711 supply voltage measured | Not yet verified | Record the measured voltage |
| HX711 DOUT voltage compatibility checked | Not yet verified | Confirm ESP32 input safety |

**Safety precaution:** Disconnect USB and all external power sources before using continuity or resistance mode. Never perform continuity testing on a powered circuit.

## 6. Combined Sensor Test Procedure

1. Connect the sensor modules to the ESP32 according to the pin table.
2. Check the wiring and power connections before supplying power.
3. Upload the combined sensor test program to the ESP32.
4. Open the Arduino IDE Serial Monitor at **115200 baud**.
5. Observe temperature and humidity readings from the DHT22.
6. Observe accelerometer and gyroscope readings from the MPU6050.
7. Compare the HW-038 ADC readings under dry and wet conditions.
8. Observe the HX711 raw readings without touching the load-cell platform.
9. Record any error messages, missing readings, or unstable measurements.
10. Perform separate stability and known-weight tests before marking the entire system as fully validated.

## 7. Sensor Integration Test Results

### 7.1 DHT22 Temperature and Humidity Sensor

**Observed results:**

- Temperature: approximately 32.50 °C
- Relative humidity: approximately 90–91%
- Temperature and humidity values were repeatedly received through the Serial Monitor.

**Observation:** The DHT22 communicated with the ESP32 during the combined test.

**Status:** Preliminary functional test passed.

**Limitations:** The readings have not been independently compared with a calibrated thermometer or hygrometer. Therefore, measurement accuracy has not been established.

### 7.2 MPU6050 Accelerometer and Gyroscope

**Observed accelerometer readings:**

- X-axis: approximately 0.72–0.86 m/s²
- Y-axis: approximately 0 m/s²
- Z-axis: approximately 10.83–11.02 m/s²

**Observed gyroscope readings:**

- X-axis: approximately -0.07 rad/s
- Y-axis: approximately -0.01 rad/s
- Z-axis: approximately 0.01 rad/s

**Observation:** Accelerometer and gyroscope values were received through the Serial Monitor. The gyroscope readings were close to zero while the sensor was stationary.

**Status:** Preliminary functional test passed.

**Limitations:** Sensor orientation, offset calibration, and controlled vibration response require further validation. The readings alone do not establish the structural condition of a real tunnel.

### 7.3 HW-038 Analog Water Sensor

**ESP32 analog input:** GPIO 34

**Observed dry-condition result:**

- ADC reading: approximately 0

**Observed wet-condition results:**

- 131
- 140
- 157
- 256
- 665

These values are examples observed during testing, not guaranteed calibration thresholds.

**Observation:** The ADC reading changed when the sensing plate came into contact with water. The dry condition generally produced a reading close to zero, while wet conditions produced different values.

**Status:** Preliminary functional test passed.

**Limitations:**

- Wet-condition readings varied.
- Repeatability under controlled conditions remains to be checked.
- Water depth and ADC response must be evaluated using repeated measurements before establishing calibration thresholds.
- The readings should not yet be interpreted as calibrated water depth or actual tunnel flooding severity.

### 7.4 HX711 and 5 kg Load Cell

**ESP32 connections:**

- DT/DOUT: GPIO 18
- SCK/CLK: GPIO 19

**Observed raw readings during the combined test:**

- Approximately -50,291 to -57,206

**Observation:** The Serial Monitor received numerical raw readings from the HX711. However, the observed variation requires further investigation.

**Status:** Communication detected; stability validation pending.

**Outstanding tests:**

1. Observe the empty-platform baseline for 30–60 seconds without touching the platform.
2. Record the minimum, maximum, and average raw readings.
3. Apply a known mass and record the response.
4. Remove the mass and check whether the reading returns near the original baseline.
5. Repeat the test to evaluate repeatability.
6. Verify the calibration factor and measured weight against known masses.
7. If the readings remain unstable, test the HX711 and load cell separately from the other sensors.

**Important:** Raw ADC values are not calibrated weight measurements. Do not mark the load-cell subsystem as fully passed until stability and known-weight validation are complete.

### 7.5 All Sensors Tested Together

The combined test program was uploaded to the ESP32, and the Serial Monitor displayed output for the DHT22, MPU6050, water sensor, and HX711.

| Sensor or Subsystem | Combined-Test Observation | Status |
|---|---|---|
| DHT22 | Temperature and humidity values received | Preliminary pass |
| MPU6050 | Accelerometer and gyroscope values received | Preliminary pass |
| HW-038 water sensor | Dry/wet ADC response observed | Preliminary pass |
| HX711 and load cell | Raw readings received; variation observed | Stability validation pending |
| Entire combined system | Output observed from the combined test program | Preliminary integration completed; full validation pending |

## 8. Issues and Observations

1. The DHT22 returned temperature readings around 32.50 °C and humidity readings around 90–91%.
2. The MPU6050 returned accelerometer readings close to the expected gravity-dominated Z-axis response when stationary, although calibration and orientation checks remain necessary.
3. The HW-038 sensor generally returned an ADC reading near zero in the dry condition and different readings in the wet condition.
4. HW-038 readings varied across wet-condition observations; controlled repeatability testing is still required.
5. HX711 raw readings varied approximately from -50,291 to -57,206 during the combined test.
6. The reason for the HX711 variation has not yet been determined. Possible factors to investigate include platform movement, mounting, wiring, electrical noise, power supply, and load-cell calibration.
7. The accuracy of the DHT22 and MPU6050 measurements has not been independently verified.
8. The actual HX711 supply voltage and DOUT logic-level compatibility must be recorded before final electrical validation.
9. The continuity and short-circuit checks must be marked complete only after the corresponding tests have actually been performed.

## 9. Follow-up Actions

- [ ] Complete and document the power-off continuity checks.
- [ ] Verify the 3.3 V and GND connections.
- [ ] Measure and record the HX711 supply voltage.
- [ ] Verify that HX711 DOUT is electrically safe for ESP32 GPIO18.
- [ ] Test the HX711 with an empty platform for 30–60 seconds.
- [ ] Test the load cell using a known mass.
- [ ] Record baseline, loaded, and unloaded readings.
- [ ] Repeat the water sensor dry/wet test under controlled conditions.
- [ ] Save a screenshot of the combined Serial Monitor output.
- [ ] Confirm that the wiring diagram matches the actual circuit.
- [ ] Save a clear photograph of the combined circuit.
- [ ] Update this log with the results of the remaining tests.

## 10. Evidence Files

The following evidence files are intended for this test session:

- `hardware/wiring_diagram/07_all_sensors_esp32.png` — combined wiring diagram
- `hardware/photos/combined_circuit.jpg` — photograph of the physical circuit
- `hardware/photos/combined_sensor_serial_output.png` — optional Serial Monitor screenshot, to be added after saving the actual screenshot

**Note:** Confirm that each file exists at the stated path before treating it as completed evidence.

## 11. Conclusion

The DHT22, MPU6050, HW-038 water sensor, and HX711/load-cell assembly were connected to the ESP32 for a preliminary combined sensor test. The Serial Monitor displayed temperature, humidity, motion-sensor, water-sensor ADC, and HX711 raw readings or status messages.

The DHT22 and MPU6050 showed preliminary communication success. The HW-038 produced different ADC readings under dry and wet conditions. The HX711 returned raw numerical readings, but their stability and response to known loads have not yet been validated.

The combined setup has therefore reached the **preliminary integration stage**, not final system validation. Electrical voltage compatibility, continuity checks, HX711 stability, known-weight response, and sensor repeatability must be verified and documented before claiming that the complete system has passed all tests.

These results represent a laboratory prototype test. They do not, by themselves, demonstrate validated structural health monitoring performance on the actual Karnaphuli Tunnel.