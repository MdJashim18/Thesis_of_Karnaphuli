#include <Wire.h>
#include <Adafruit_MPU6050.h>
#include <Adafruit_Sensor.h>
#include <math.h>

Adafruit_MPU6050 mpu;

const int SAMPLE_COUNT = 500;

struct Sample {
  uint32_t t_us;
  float ax, ay, az;
  float gx, gy, gz;
  float temp;
};

static Sample buf[SAMPLE_COUNT];

void runTest(const char *testName, uint32_t intervalUs, mpu6050_bandwidth_t bw) {
  mpu.setFilterBandwidth(bw);
  delay(50);

  Serial.print("# Test: ");
  Serial.println(testName);
  Serial.print("# Rate_Hz: ");
  Serial.println(1000000.0f / intervalUs, 1);
  Serial.println("# Sampling...");

  uint32_t start = micros();
  uint32_t next = start;

  for (int i = 0; i < SAMPLE_COUNT; i++) {
    while ((int32_t)(micros() - next) < 0) {}
    uint32_t t = micros() - start;
    next += intervalUs;

    sensors_event_t a, g, temp;
    mpu.getEvent(&a, &g, &temp);

    buf[i] = { t,
               a.acceleration.x, a.acceleration.y, a.acceleration.z,
               g.gyro.x, g.gyro.y, g.gyro.z,
               temp.temperature };
  }

  Serial.println("sample,timestamp_ms,ax_m_s2,ay_m_s2,az_m_s2,gx_rad_s,gy_rad_s,gz_rad_s,temp_c,accel_magnitude_m_s2");
  for (int i = 0; i < SAMPLE_COUNT; i++) {
    const Sample &s = buf[i];
    float mag = sqrtf(s.ax * s.ax + s.ay * s.ay + s.az * s.az);
    Serial.printf("%d,%.3f,%.4f,%.4f,%.4f,%.4f,%.4f,%.4f,%.2f,%.4f\n",
                  i + 1, s.t_us / 1000.0f,
                  s.ax, s.ay, s.az, s.gx, s.gy, s.gz, s.temp, mag);
  }

  while (Serial.available()) Serial.read();
  Serial.println("# TEST COMPLETE");
  Serial.println("# Type s for stationary or v for vibration.");
}

void setup() {
  Serial.begin(115200);
  delay(1500);

  Wire.begin(21, 22);

  if (!mpu.begin(0x68, &Wire)) {
    Serial.println("ERROR: MPU6050 initialization failed.");
    while (true) delay(1000);
  }

  Wire.setClock(400000);

  mpu.setAccelerometerRange(MPU6050_RANGE_8_G);
  mpu.setGyroRange(MPU6050_RANGE_500_DEG);

  Serial.println("MPU6050 READY");
  Serial.println("Keep sensor still, then type s.");
  Serial.println("For tap/vibration test, type v.");
}

void loop() {
  if (Serial.available() > 0) {
    char c = Serial.read();
    if (c == 's' || c == 'S') {
      runTest("stationary", 20000, MPU6050_BAND_21_HZ);  // 50 Hz
    } else if (c == 'v' || c == 'V') {
      runTest("vibration", 5000, MPU6050_BAND_94_HZ);    // 200 Hz
    }
  }
}