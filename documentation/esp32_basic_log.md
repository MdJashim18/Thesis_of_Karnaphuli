# ESP32 Basic Test Log — Day 3

## 1. Hardware Information
- Microcontroller: ESP32
- Board: DOIT ESP32 DEVKIT V1
- Connection: USB

## 2. Software Information
- Arduino IDE Version: 2.3.6
- ESP32 Board Package: ESP32 by Espressif Systems
- COM Port: COM5
- Serial Baud Rate: 115200

## 3. Test 1 — Onboard LED Blink
- Sketch: `firmware/01_blink/01_blink.ino`
- GPIO Pin: GPIO 2
- ON Duration: 500 ms
- OFF Duration: 500 ms
- Compilation: Successful
- Upload: Successful
- Observation: Onboard LED blinked successfully.

## 4. Test 2 — Serial Monitor Uptime
- Sketch: `firmware/02_serial/02_serial.ino`
- Compilation: Successful
- Upload: Successful
- Baud Rate: 115200
- Output: Uptime printed approximately every 1 second.

### Sample Output
```text
Uptime: 84999 ms
Uptime: 85999 ms
Uptime: 86999 ms
Uptime: 87999 ms
Uptime: 88999 ms
```

## 5. Conclusion
Both the LED blink test and Serial Monitor uptime test were completed successfully. The ESP32 successfully executed the uploaded firmware and printed uptime data through serial communication.

## 6. Evidence
- `hardware/photos/blink_test.jpg`
- Serial Monitor screenshot
- Successful upload screenshot