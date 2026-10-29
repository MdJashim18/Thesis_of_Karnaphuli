#include <WiFi.h>
#include <HTTPClient.h>
#include <Wire.h>
#include <DHT.h>
#include <Adafruit_MPU6050.h>
#include <Adafruit_Sensor.h>
#include <Preferences.h>
#include "HX711.h"

// ========== WIFI ==========
const char* WIFI_SSID = "Bachelor";
const char* WIFI_PASSWORD = "12344321";
const char* API_URL = "http://192.168.0.102:5000/telemetry";

// ========== DEVICE ==========
const char* DEVICE_ID = "ESP32-GW-LAB-001";
const char* GATEWAY_ID = "gateway01";
const char* ZONE_ID = "LAB_PROTOTYPE";

// ========== PINS ==========
#define DHT_PIN 4
#define DHT_TYPE DHT22
#define WATER_PIN 34
#define HX711_DOUT 18
#define HX711_SCK 19

// ========== OBJECTS ==========
DHT dht(DHT_PIN, DHT_TYPE);
Adafruit_MPU6050 mpu;
HX711 scale;
Preferences prefs;

bool mpuReady = false;

// ========== LOAD CALIBRATION (flash-e save thake) ==========
long  loadOffset = 0;     // no-load raw value
float loadScale  = 0.0;   // raw units per kg (0 = calibrate kora hoy ni)

// ========== TIMERS ==========
unsigned long lastPublish = 0;
unsigned long lastDHTRead = 0;
unsigned long lastWiFiAttempt = 0;

const unsigned long PUBLISH_INTERVAL = 1000;
const unsigned long DHT_INTERVAL = 2000;
const unsigned long WIFI_RETRY = 5000;

// ========== LAST DHT READINGS ==========
float temperature = 0.0;
float humidity = 0.0;
bool dhtValid = false;

// ========== WIFI ==========
bool connectWiFi() {
  Serial.println("Connecting to Wi-Fi...");
  WiFi.mode(WIFI_STA);
  WiFi.setSleep(false);
  WiFi.begin(WIFI_SSID, WIFI_PASSWORD);

  unsigned long start = millis();
  while (WiFi.status() != WL_CONNECTED && millis() - start < 20000) {
    delay(500);
    Serial.print(".");
  }
  Serial.println();

  if (WiFi.status() == WL_CONNECTED) {
    Serial.println("Wi-Fi connected!");
    Serial.print("ESP32 IP: ");
    Serial.println(WiFi.localIP());
    return true;
  }
  Serial.println("Wi-Fi connection failed.");
  return false;
}

// ========== CALIBRATION ==========
void saveCalibration() {
  prefs.putLong("offset", loadOffset);
  prefs.putFloat("scale", loadScale);
}

// Serial commands:
//   t       -> tare (load cell-e kichu nai)
//   c500    -> known weight (gram) rekhe calibrate
//   r       -> reset
void handleSerial() {
  if (!Serial.available()) return;

  String cmd = Serial.readStringUntil('\n');
  cmd.trim();
  if (cmd.length() == 0) return;

  if (!scale.is_ready()) {
    Serial.println("HX711 not ready.");
    return;
  }

  if (cmd == "t") {
    loadOffset = scale.read_average(10);
    saveCalibration();
    Serial.printf("Tare done. Offset = %ld\n", loadOffset);

  } else if (cmd.startsWith("c")) {
    float grams = cmd.substring(1).toFloat();
    if (grams <= 0) {
      Serial.println("Usage: c500 (weight in grams)");
      return;
    }
    long raw = scale.read_average(10);
    loadScale = (float)(raw - loadOffset) / (grams / 1000.0);
    saveCalibration();
    Serial.printf("Calibrated. Raw=%ld Offset=%ld Scale=%.2f raw/kg\n",
                  raw, loadOffset, loadScale);

  } else if (cmd == "r") {
    loadOffset = 0;
    loadScale = 0.0;
    saveCalibration();
    Serial.println("Calibration reset.");

  } else {
    Serial.println("Commands: t | c<grams> | r");
  }
}

// ========== SETUP ==========
void setup() {
  Serial.begin(115200);
  delay(1000);

  Serial.println();
  Serial.println("================================");
  Serial.println("Karnaphuli Tunnel SHM");
  Serial.println("HTTP Telemetry + Load Calibration");
  Serial.println("Serial cmds: t | c<grams> | r");
  Serial.println("================================");

  analogReadResolution(12);

  prefs.begin("loadcal", false);
  loadOffset = prefs.getLong("offset", 0);
  loadScale = prefs.getFloat("scale", 0.0);
  Serial.printf("Load offset=%ld scale=%.2f\n", loadOffset, loadScale);

  dht.begin();

  Wire.begin(21, 22);
  if (mpu.begin()) {
    mpuReady = true;
    Serial.println("MPU6050 detected.");
  } else {
    Serial.println("WARNING: MPU6050 not detected.");
  }

  scale.begin(HX711_DOUT, HX711_SCK);
  if (scale.wait_ready_timeout(1000)) {
    Serial.println("HX711 detected.");
  } else {
    Serial.println("WARNING: HX711 not ready.");
  }

  connectWiFi();

  temperature = dht.readTemperature();
  humidity = dht.readHumidity();
  if (!isnan(temperature) && !isnan(humidity)) {
    dhtValid = true;
    lastDHTRead = millis();
  } else {
    temperature = 0.0;
    humidity = 0.0;
  }
}

// ========== LOOP ==========
void loop() {
  handleSerial();

  unsigned long now = millis();

  if (WiFi.status() != WL_CONNECTED) {
    if (now - lastWiFiAttempt >= WIFI_RETRY) {
      lastWiFiAttempt = now;
      connectWiFi();
    }
    return;
  }

  if (now - lastPublish < PUBLISH_INTERVAL) return;
  lastPublish = now;

  // ----- DHT22 -----
  if (now - lastDHTRead >= DHT_INTERVAL) {
    lastDHTRead = now;
    float t = dht.readTemperature();
    float h = dht.readHumidity();
    if (!isnan(t) && !isnan(h)) {
      temperature = t;
      humidity = h;
      dhtValid = true;
    } else {
      Serial.println("WARNING: DHT22 reading failed.");
    }
  }

  // ----- MPU6050 -----
  float ax = 0.0, ay = 0.0, az = 0.0;
  bool mpuValid = false;
  if (mpuReady) {
    sensors_event_t accel, gyro, sensorTemp;
    mpu.getEvent(&accel, &gyro, &sensorTemp);
    ax = accel.acceleration.x;
    ay = accel.acceleration.y;
    az = accel.acceleration.z;
    mpuValid = true;
  }

  // ----- Water sensor -----
  int waterRaw = analogRead(WATER_PIN);

  // ----- HX711 -----
  long loadRaw = 0;
  bool hx711Valid = scale.is_ready();
  if (hx711Valid) {
    loadRaw = scale.read_average(3);
  }

  bool loadCalibrated = (loadScale != 0.0);
  float loadKg = 0.0;
  if (hx711Valid && loadCalibrated) {
    loadKg = (float)(loadRaw - loadOffset) / loadScale;
  }

  const char* quality;
  if (!(dhtValid && mpuValid && hx711Valid)) {
    quality = "degraded";
  } else if (!loadCalibrated) {
    quality = "partial";
  } else {
    quality = "ok";
  }

  // ----- JSON -----
  char payload[640];
  snprintf(
    payload, sizeof(payload),
    "{"
      "\"device_id\":\"%s\","
      "\"gateway_id\":\"%s\","
      "\"zone_id\":\"%s\","
      "\"temperature\":%.2f,"
      "\"humidity\":%.2f,"
      "\"accel_x\":%.3f,"
      "\"accel_y\":%.3f,"
      "\"accel_z\":%.3f,"
      "\"water_raw\":%d,"
      "\"load_raw\":%ld,"
      "\"load_kg\":%.3f,"
      "\"dht_valid\":%s,"
      "\"mpu_valid\":%s,"
      "\"hx711_valid\":%s,"
      "\"quality_flag\":\"%s\""
    "}",
    DEVICE_ID, GATEWAY_ID, ZONE_ID,
    temperature, humidity, ax, ay, az,
    waterRaw, loadRaw, loadKg,
    dhtValid ? "true" : "false",
    mpuValid ? "true" : "false",
    hx711Valid ? "true" : "false",
    quality);

  // ----- HTTP POST -----
  HTTPClient http;
  http.setTimeout(5000);
  http.setReuse(false);

  if (!http.begin(API_URL)) {
    Serial.println("ERROR: Could not initialize HTTP.");
    return;
  }
  http.addHeader("Content-Type", "application/json");

  int httpCode = http.POST((uint8_t*)payload, strlen(payload));

  Serial.println();
  Serial.println("----- TELEMETRY -----");
  Serial.printf("Temp: %.2f C | Hum: %.2f %%\n", temperature, humidity);
  Serial.printf("Accel: %.3f %.3f %.3f\n", ax, ay, az);
  Serial.printf("Water raw: %d\n", waterRaw);
  Serial.printf("Load raw: %ld | Load kg: %.3f %s\n", loadRaw, loadKg,
                loadCalibrated ? "" : "(NOT calibrated)");
  Serial.printf("Quality: %s\n", quality);
  Serial.printf("HTTP status: %d\n", httpCode);

  if (httpCode > 0) {
    Serial.print("API response: ");
    Serial.println(http.getString());
  } else {
    Serial.print("HTTP error: ");
    Serial.println(http.errorToString(httpCode));
  }
  Serial.println("---------------------");

  http.end();
}