# MPU6050 Validation Log

## 1. Objective

Validate communication between the ESP32 development board and the MPU6050 motion sensor, and record stationary and vibration test results for the project.

## 2. Hardware Setup

- **Microcontroller:** ESP32
- **Sensor:** MPU6050
- **Communication protocol:** I²C
- **Detected I²C address:** `0x68`
- **Serial Monitor baud rate:** `115200`

### Wiring

| MPU6050 pin | ESP32 pin |
|---|---|
| VCC | 3V3 |
| GND | GND |
| SDA | GPIO 21 |
| SCL | GPIO 22 |

## 3. Communication Test

**Status: PASS**

The I²C scanner detected a device at address `0x68`.

Observed output:

```text
I2C Scanner Started
Found I2C device at 0x68
Total devices: 1
```

A Serial test also confirmed that serial output was working. The MPU6050 read test subsequently produced sensor readings.

## 4. Sampling Configuration

The vibration capture output reported:

- **Reported sampling rate:** 200 Hz
- **Target sample count:** 500 samples
- **Approximate interval between samples:** 5 ms
- **Recorded duration:** approximately 2.5 seconds

Use the actual configuration of the sketch when recording future tests. If the sketch settings change, update this section accordingly.

## 5. Stationary Test

**Status: PENDING VALIDATION**

Procedure:

1. Place the MPU6050 on a flat, stable surface.
2. Keep the sensor still.
3. Send `s` in the Serial Monitor if prompted by the sketch.
4. Capture all 500 samples.
5. Save the CSV data as `data/raw/mpu6050_stationary.csv`.

Record the result after inspecting the captured data:

- Sample count: Pending
- Unexpected movement/spikes: Pending
- Result: Pending

Do not mark this test as passed until the recorded data has been checked.

## 6. Vibration Test

**Status: CAPTURE COMPLETED; VIBRATION RESPONSE NOT YET VERIFIED**

A vibration capture was recorded with the following metadata:

- Test label: `vibration`
- Reported sampling rate: 200 Hz
- Samples recorded: 500
- Approximate capture duration: 2.5 seconds

The supplied readings showed acceleration values that remained relatively stable, with acceleration magnitude approximately around 10.84–11.03 m/s². Clear vibration-related spikes were not evident in the supplied capture. Therefore, the capture process completed, but the vibration response has **not yet been validated**.

Recommended retest:

1. Secure the sensor and wiring so they cannot disconnect.
2. Start a new vibration capture using `v`.
3. Gently tap or vibrate the surface holding the sensor during the capture.
4. Check whether acceleration and/or gyroscope readings change noticeably during the stimulus.
5. Save the verified raw CSV data as `data/raw/mpu6050_vibration.csv`.

Avoid hitting the sensor or board directly or using force that could damage the hardware.

## 7. Data Storage

Recommended project structure:

```text
project/
├── data/
│   └── raw/
│       ├── mpu6050_stationary.csv
│       └── mpu6050_vibration.csv
└── documentation/  
    ├── stationary_test.png
    │── vibration_test.png
    └── mpu6050_validation_log.md
├── hardware/
│   └── photos/
│       ├── mpu6050_wiring1.png
│       └── mpu6050_wiring2.png
```

For analysis-ready CSV files, keep the CSV header and sensor data rows. Remove status/metadata lines beginning with `#` unless the analysis script is explicitly designed to parse them.

## 8. Evidence to Collect

- [ ] Photo of the ESP32–MPU6050 wiring
- [ ] Screenshot showing the I²C scanner detecting `0x68`
- [ ] Stationary test output or CSV
- [ ] Vibration test output or CSV showing a deliberate stimulus
- [ ] Confirmation that the saved CSV files contain the expected number of samples

## 9. Current Summary

| Check | Status |
|---|---|
| ESP32 serial output | Pass |
| MPU6050 detected over I²C at `0x68` | Pass |
| MPU6050 sensor readings received | Pass |
| Stationary dataset inspected | Pending |
| Vibration dataset captured | Pass — capture only |
| Vibration response verified | Pending |

## 10. Notes

This log records only the tests and observations currently available. Do not report stationary stability or vibration detection as validated until the corresponding data has been inspected and the result documented.
