# Day 6 — MPU6050 I²C Validation Log

## Objective
Verify I²C communication between the MPU6050 sensor and ESP32 DOIT DEVKIT V1.

## Hardware
- Microcontroller: ESP32 DOIT DEVKIT V1
- Sensor: MPU6050
- Interface: I²C

## Wiring
- VCC → 3V3
- GND → GND
- SDA → GPIO 21
- SCL → GPIO 22

## Test Configuration
- Scanner sketch: `firmware/04_i2c_scanner/04_i2c_scanner.ino`
- Serial baud rate: 115200

## Observed Result
```text
Found I2C device at 0x68
Total devices: 1
```

## Result
**Status: PASS — I²C device detected.**

The scanner detected one I²C device at address `0x68`. This confirms that the device responds on the I²C bus. Accelerometer and gyroscope measurements still require separate testing.

## Evidence
- `hardware/wiring_diagram/04_mpu6050_esp32.png`
- `hardware/photos/mpu6050_wiring.jpg`

## Next Step
Read and verify accelerometer and gyroscope measurements from the MPU6050.
