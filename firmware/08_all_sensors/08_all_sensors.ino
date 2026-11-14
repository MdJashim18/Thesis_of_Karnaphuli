
#include <Wire.h>
#include <DHT.h>
#include <Adafruit_MPU6050.h>
#include <Adafruit_Sensor.h>
#include "HX711.h"
#include <math.h>

// ---------- Device information ----------
const char* DEVICE_ID = "ESP32-GW-LAB-001";
const char* ZONE_ID   = "LAB_PROTOTYPE";

// ---------- ESP32 pin configuration ----------
#define DHTPIN       4
#define DHTTYPE      DHT22
#define WATER_PIN    34
#define HX711_DOUT   18
#define HX711_SCK    19

// ---------- Load-cell calibration ----------
// Keep false until calibration has been validated
// with known masses.
const bool LOAD_CELL_CALIBRATED = false;

// Replace 1.0 only with your verified calibration
// factor. The existing factor must match the HX711
// library and the units used in your calibration.
const float HX711_CALIBRATION_FACTOR = 1.0f;

// ---------- Sensor objects ----------
DHT dht(DHTPIN, DHTTYPE);
Adafruit_MPU6050 mpu;
HX711 scale;

bool mpuOK = false;
bool hx711OK = false;

unsigned long lastReadTime = 0;
const unsigned long READ_INTERVAL_MS = 2000;

// ---------- JSON helper functions ----------
void printJsonFloat(float value, int decimals = 2) {
  if (isnan(value) || isinf(value)) {
    Serial.print("null");
  } else {
    Serial.print(value, decimals);
  }
}

void printJsonLong(long value) {
  Serial.print(value);
}

void setup() {
  Serial.begin(115200);
  delay(1000);

  Serial.println();
  Serial.println("Karnaphuli SHM - Day 13 Combined Firmware");

  // DHT22
  dht.begin();
  Serial.println("DHT22 initialized");

  // MPU6050: SDA = GPIO21, SCL = GPIO22
  Wire.begin(21, 22);
  mpuOK = mpu.begin(0x68);

  if (mpuOK) {
    Serial.println("MPU6050 initialized");
  } else {
    Serial.println("WARNING: MPU6050 not detected");
  }

  // Water sensor
  analogReadResolution(12);
  pinMode(WATER_PIN, INPUT);
  Serial.println("HW-038 configured on GPIO34");

  // HX711: DOUT = GPIO18, SCK = GPIO19
  scale.begin(HX711_DOUT, HX711_SCK);
  hx711OK = scale.is_ready();

  if (hx711OK) {
    Serial.println("HX711 detected");

    if (LOAD_CELL_CALIBRATED) {
      scale.set_scale(HX711_CALIBRATION_FACTOR);
      scale.tare();
      Serial.println("HX711 tare completed");
    } else {
      Serial.println(
        "HX711 raw mode: load calibration not verified"
      );
    }
  } else {
    Serial.println("WARNING: HX711 not ready at startup");
  }

  Serial.println("JSON stream starts below:");
}

void loop() {
  unsigned long now = millis();

  if (now - lastReadTime < READ_INTERVAL_MS) {
    return;
  }
  lastReadTime = now;

  // ---------- Read DHT22 ----------
  float temperature = dht.readTemperature();
  float humidity = dht.readHumidity();

  bool dhtOK = !isnan(temperature) &&
               !isnan(humidity) &&
               !isinf(temperature) &&
               !isinf(humidity);

  // ---------- Read MPU6050 ----------
  sensors_event_t accel;
  sensors_event_t gyro;
  sensors_event_t mpuTemp;

  float ax = NAN;
  float ay = NAN;
  float az = NAN;
  float gx = NAN;
  float gy = NAN;
  float gz = NAN;

  if (mpuOK) {
    mpu.getEvent(&accel, &gyro, &mpuTemp);

    ax = accel.acceleration.x;
    ay = accel.acceleration.y;
    az = accel.acceleration.z;

    gx = gyro.gyro.x;
    gy = gyro.gyro.y;
    gz = gyro.gyro.z;
  }

  bool motionOK = mpuOK &&
                  !isnan(ax) && !isnan(ay) && !isnan(az) &&
                  !isnan(gx) && !isnan(gy) && !isnan(gz);

  // ---------- Read water sensor ----------
  int waterRaw = analogRead(WATER_PIN);

  // ---------- Read HX711 ----------
  bool loadReady = scale.is_ready();
  long loadRaw = 0;
  float loadKg = NAN;

  if (loadReady) {
    loadRaw = scale.read_average(5);

    if (LOAD_CELL_CALIBRATED) {
      // Assumes your verified calibration factor
      // produces readings in grams.
      float weightGrams = scale.get_units(5);
      loadKg = weightGrams / 1000.0f;
    }
  }

  // ---------- Determine data quality ----------
  bool allValid = dhtOK &&
                  motionOK &&
                  loadReady &&
                  LOAD_CELL_CALIBRATED &&
                  !isnan(loadKg) &&
                  !isinf(loadKg);

  const char* qualityFlag = allValid ? "valid" : "partial";

  // ---------- Output one JSON object per line ----------
  Serial.print("{");

  Serial.print("\"device_id\":\"");
  Serial.print(DEVICE_ID);
  Serial.print("\",");

  Serial.print("\"zone_id\":\"");
  Serial.print(ZONE_ID);
  Serial.print("\",");

  Serial.print("\"timestamp_ms\":");
  Serial.print(now);
  Serial.print(",");

  Serial.print("\"temperature\":");
  printJsonFloat(dhtOK ? temperature : NAN);
  Serial.print(",");

  Serial.print("\"humidity\":");
  printJsonFloat(dhtOK ? humidity : NAN);
  Serial.print(",");

  Serial.print("\"accel_x\":");
  printJsonFloat(motionOK ? ax : NAN);
  Serial.print(",");

  Serial.print("\"accel_y\":");
  printJsonFloat(motionOK ? ay : NAN);
  Serial.print(",");

  Serial.print("\"accel_z\":");
  printJsonFloat(motionOK ? az : NAN);
  Serial.print(",");

  Serial.print("\"gyro_x\":");
  printJsonFloat(motionOK ? gx : NAN);
  Serial.print(",");

  Serial.print("\"gyro_y\":");
  printJsonFloat(motionOK ? gy : NAN);
  Serial.print(",");

  Serial.print("\"gyro_z\":");
  printJsonFloat(motionOK ? gz : NAN);
  Serial.print(",");

  Serial.print("\"water_raw\":");
  printJsonLong(waterRaw);
  Serial.print(",");

  Serial.print("\"load_raw\":");
  if (loadReady) {
    printJsonLong(loadRaw);
  } else {
    Serial.print("null");
  }
  Serial.print(",");

  Serial.print("\"load_kg\":");
  printJsonFloat(loadKg, 3);
  Serial.print(",");

  Serial.print("\"quality_flag\":\"");
  Serial.print(qualityFlag);
  Serial.println("\"}");
}
