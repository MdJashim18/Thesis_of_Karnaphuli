
#include <Wire.h>

#define MPU_ADDR 0x68

void setup() {
  Serial.begin(115200);
  delay(1000);

  Wire.begin(21, 22);

  // Wake up MPU6050
  Wire.beginTransmission(MPU_ADDR);
  Wire.write(0x6B);
  Wire.write(0x00);
  byte error = Wire.endTransmission();

  if (error == 0) {
    Serial.println("MPU6050 initialized successfully!");
  } else {
    Serial.println("MPU6050 initialization failed!");
    while (true) {
      delay(1000);
    }
  }
}

void loop() {
  Wire.beginTransmission(MPU_ADDR);
  Wire.write(0x3B);
  byte error = Wire.endTransmission(false);

  if (error != 0) {
    Serial.println("I2C read error!");
    delay(1000);
    return;
  }

  byte received = Wire.requestFrom(MPU_ADDR, 14, true);

  if (received == 14) {
    int16_t ax = (Wire.read() << 8) | Wire.read();
    int16_t ay = (Wire.read() << 8) | Wire.read();
    int16_t az = (Wire.read() << 8) | Wire.read();

    Wire.read(); // Temperature
    Wire.read(); // Temperature

    int16_t gx = (Wire.read() << 8) | Wire.read();
    int16_t gy = (Wire.read() << 8) | Wire.read();
    int16_t gz = (Wire.read() << 8) | Wire.read();

    Serial.print("Accel (g): X=");
    Serial.print(ax / 16384.0, 3);
    Serial.print(" Y=");
    Serial.print(ay / 16384.0, 3);
    Serial.print(" Z=");
    Serial.println(az / 16384.0, 3);

    Serial.print("Gyro (deg/s): X=");
    Serial.print(gx / 131.0, 3);
    Serial.print(" Y=");
    Serial.print(gy / 131.0, 3);
    Serial.print(" Z=");
    Serial.println(gz / 131.0, 3);

    Serial.println("--------------------------");
  } else {
    Serial.println("Incomplete sensor data!");
  }

  delay(1000);
}
