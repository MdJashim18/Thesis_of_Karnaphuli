
#include <WiFi.h>
#include <HTTPClient.h>
#include <Wire.h>
#include <DHT.h>
#include <Adafruit_MPU6050.h>
#include <Adafruit_Sensor.h>
#include <Preferences.h>
#include "HX711.h"

#include <time.h>
#include <sys/time.h>
#include <stdint.h>
#include <math.h>

// ==================================================
// WIFI CONFIGURATION
// ==================================================

const char* WIFI_SSID = "Bachelor";
const char* WIFI_PASSWORD = "12344321";

const char* API_URL =
  "http://192.168.0.103:5000/telemetry";


// const char* WIFI_SSID = "Mohammad Jashim Uddin";
// const char* WIFI_PASSWORD = "Baiman_k_maf_korte_nei";

// const char* API_URL =
//   "http://10.111.183.37:5000/telemetry";

// ==================================================
// DEVICE CONFIGURATION
// ==================================================

const char* DEVICE_ID = "ESP32-GW-LAB-001";
const char* GATEWAY_ID = "gateway01";
const char* ZONE_ID = "LAB_PROTOTYPE";

const char* SESSION_ID = "SHM-TEST-001";

// ==================================================
// SENSOR PINS
// ==================================================

#define DHT_PIN 4
#define DHT_TYPE DHT22

#define WATER_PIN 34

#define HX711_DOUT 18
#define HX711_SCK 19

// ==================================================
// OBJECTS
// ==================================================

DHT dht(DHT_PIN, DHT_TYPE);

Adafruit_MPU6050 mpu;

HX711 scale;

Preferences prefs;

bool mpuReady = false;

// ==================================================
// LOAD CELL CALIBRATION
// ==================================================

long loadOffset = 0;

float loadScale = 0.0;

// ==================================================
// RELIABILITY MONITORING
// ==================================================

uint32_t sequenceNumber = 0;

uint32_t wifiReconnectCount = 0;

bool hasConnectedOnce = false;

bool ntpSynced = false;

// ==================================================
// TIMERS
// ==================================================

unsigned long lastPublish = 0;

unsigned long lastDHTRead = 0;

unsigned long lastWiFiAttempt = 0;

const unsigned long PUBLISH_INTERVAL = 1000;

const unsigned long DHT_INTERVAL = 2000;

const unsigned long WIFI_RETRY = 5000;

// ==================================================
// SENSOR DATA
// ==================================================

float temperature = 0.0;

float humidity = 0.0;

bool dhtValid = false;

// ==================================================
// NTP TIMESTAMP
// ==================================================

uint64_t getDeviceTimestampMs() {

  struct timeval tv;

  gettimeofday(&tv, nullptr);

  return (uint64_t)tv.tv_sec * 1000ULL
         + tv.tv_usec / 1000;
}

// ==================================================
// WIFI CONNECTION
// ==================================================

bool connectWiFi() {

  Serial.println();
  Serial.println("Connecting to Wi-Fi...");

  WiFi.mode(WIFI_STA);

  WiFi.setSleep(false);

  WiFi.begin(WIFI_SSID, WIFI_PASSWORD);

  unsigned long start = millis();

  while (
    WiFi.status() != WL_CONNECTED &&
    millis() - start < 20000
  ) {

    delay(500);

    Serial.print(".");
  }

  Serial.println();

  if (WiFi.status() == WL_CONNECTED) {

    if (hasConnectedOnce) {

      wifiReconnectCount++;

      Serial.printf(
        "Wi-Fi Reconnection Event: %lu\n",
        (unsigned long)wifiReconnectCount
      );
    }

    hasConnectedOnce = true;

    Serial.println("Wi-Fi connected!");

    Serial.print("ESP32 IP: ");

    Serial.println(WiFi.localIP());

    return true;
  }

  Serial.println("Wi-Fi connection failed.");

  return false;
}

// ==================================================
// NTP TIME SYNCHRONIZATION
// ==================================================

bool synchronizeTime() {

  Serial.println();
  Serial.println("Synchronizing UTC clock...");

  configTime(
    0,
    0,
    "pool.ntp.org",
    "time.google.com"
  );

  unsigned long start = millis();

  while (millis() - start < 20000) {

    time_t now = time(nullptr);

    if (now >= 1700000000) {

      ntpSynced = true;

      Serial.println("NTP synchronization successful.");

      Serial.print("UTC Time: ");

      Serial.println(ctime(&now));

      return true;
    }

    delay(500);

    Serial.print(".");
  }

  ntpSynced = false;

  Serial.println();

  Serial.println("WARNING: NTP synchronization failed.");

  return false;
}

// ==================================================
// LOAD CELL CALIBRATION SAVE
// ==================================================

void saveCalibration() {

  prefs.putLong("offset", loadOffset);

  prefs.putFloat("scale", loadScale);
}

// ==================================================
// SERIAL COMMANDS
//
// t      = Tare
// c500   = Calibrate using 500g
// r      = Reset calibration
// ==================================================

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

    Serial.printf(
      "Tare done. Offset = %ld\n",
      loadOffset
    );

  }

  else if (cmd.startsWith("c")) {

    float grams = cmd.substring(1).toFloat();

    if (grams <= 0) {

      Serial.println("Usage: c500");

      return;
    }

    long raw = scale.read_average(10);

    loadScale =
      (float)(raw - loadOffset) / (grams / 1000.0);

    if (fabs(loadScale) < 0.001) {

      Serial.println("Invalid calibration factor.");

      return;
    }

    saveCalibration();

    Serial.printf(
      "Calibrated. Raw=%ld Offset=%ld Scale=%.2f raw/kg\n",
      raw,
      loadOffset,
      loadScale
    );

  }

  else if (cmd == "r") {

    loadOffset = 0;

    loadScale = 0.0;

    saveCalibration();

    Serial.println("Calibration reset.");

  }

  else {

    Serial.println("Commands: t | c<grams> | r");
  }
}

// ==================================================
// SETUP
// ==================================================

void setup() {

  Serial.begin(115200);

  delay(1000);

  Serial.println();

  Serial.println("======================================");

  Serial.println("KARNAPHULI TUNNEL SHM");

  Serial.println("HTTP TELEMETRY + RELIABILITY MONITOR");

  Serial.println("NTP + SEQUENCE + WIFI TRACKING");

  Serial.println("Serial Commands: t | c500 | r");

  Serial.println("======================================");

  analogReadResolution(12);

  // ----- LOAD CALIBRATION -----

  prefs.begin("loadcal", false);

  loadOffset = prefs.getLong("offset", 0);

  loadScale = prefs.getFloat("scale", 0.0);

  Serial.printf(
    "Load offset=%ld scale=%.2f\n",
    loadOffset,
    loadScale
  );

  // ----- DHT22 -----

  dht.begin();

  // ----- MPU6050 -----

  Wire.begin(21, 22);

  if (mpu.begin()) {

    mpuReady = true;

    Serial.println("MPU6050 detected.");

  }

  else {

    Serial.println("WARNING: MPU6050 not detected.");
  }

  // ----- HX711 -----

  scale.begin(
    HX711_DOUT,
    HX711_SCK
  );

  if (scale.wait_ready_timeout(1000)) {

    Serial.println("HX711 detected.");

  }

  else {

    Serial.println("WARNING: HX711 not ready.");
  }

  // ----- WIFI -----

  connectWiFi();

  // ----- NTP -----

  if (WiFi.status() == WL_CONNECTED) {

    synchronizeTime();
  }

  // ----- INITIAL DHT READING -----

  temperature = dht.readTemperature();

  humidity = dht.readHumidity();

  if (
    !isnan(temperature) &&
    !isnan(humidity)
  ) {

    dhtValid = true;

    lastDHTRead = millis();

  }

  else {

    temperature = 0.0;

    humidity = 0.0;

    dhtValid = false;
  }

  Serial.println();

  Serial.println("System initialization completed.");

  Serial.println("Waiting for telemetry cycle...");
}

// ==================================================
// MAIN LOOP
// ==================================================

void loop() {

  // ----- SERIAL COMMANDS -----

  handleSerial();

  unsigned long now = millis();

  // ----- WIFI RECONNECTION -----

  if (WiFi.status() != WL_CONNECTED) {

    if (
      now - lastWiFiAttempt >= WIFI_RETRY
    ) {

      lastWiFiAttempt = now;

      if (connectWiFi()) {

        // Re-sync time after Wi-Fi recovery
        synchronizeTime();
      }
    }

    return;
  }

  // ----- PUBLISH INTERVAL -----

  if (
    now - lastPublish < PUBLISH_INTERVAL
  ) {

    return;
  }

  lastPublish = now;

  // ==================================================
  // DHT22
  // ==================================================

  if (
    now - lastDHTRead >= DHT_INTERVAL
  ) {

    lastDHTRead = now;

    float t = dht.readTemperature();

    float h = dht.readHumidity();

    if (
      !isnan(t) &&
      !isnan(h)
    ) {

      temperature = t;

      humidity = h;

      dhtValid = true;
    }

    else {

      Serial.println("WARNING: DHT22 reading failed.");
    }
  }

  // ==================================================
  // MPU6050
  // ==================================================

  float ax = 0.0;

  float ay = 0.0;

  float az = 0.0;

  bool mpuValid = false;

  if (mpuReady) {

    sensors_event_t accel;

    sensors_event_t gyro;

    sensors_event_t sensorTemp;

    mpu.getEvent(
      &accel,
      &gyro,
      &sensorTemp
    );

    ax = accel.acceleration.x;

    ay = accel.acceleration.y;

    az = accel.acceleration.z;

    mpuValid = true;
  }

  // ==================================================
  // WATER SENSOR
  // ==================================================

  int waterRaw = analogRead(WATER_PIN);

  // ==================================================
  // HX711
  // ==================================================

  long loadRaw = 0;

  bool hx711Valid = scale.is_ready();

  if (hx711Valid) {

    loadRaw = scale.read_average(3);
  }

  bool loadCalibrated = (fabs(loadScale) > 0.001);

  float loadKg = 0.0;

  if (
    hx711Valid &&
    loadCalibrated
  ) {

    loadKg =
      (float)(loadRaw - loadOffset) / loadScale;
  }

  // ==================================================
  // QUALITY FLAG
  // ==================================================

  const char* quality;

  if (
    !(dhtValid && mpuValid && hx711Valid)
  ) {

    quality = "degraded";
  }

  else if (!loadCalibrated) {

    quality = "partial";
  }

  else {

    quality = "ok";
  }

  // ==================================================
  // DEVICE TIMESTAMP
  // ==================================================

  uint64_t deviceTimestamp = 0;

  if (ntpSynced) {

    deviceTimestamp = getDeviceTimestampMs();
  }

  // ==================================================
  // JSON PAYLOAD
  // ==================================================

  char payload[1024];

  int payloadLength = snprintf(
    payload,
    sizeof(payload),

    "{"

      "\"device_id\":\"%s\","

      "\"gateway_id\":\"%s\","

      "\"zone_id\":\"%s\","

      "\"session_id\":\"%s\","

      "\"sequence_number\":%lu,"

      "\"device_timestamp_ms\":%llu,"

      "\"wifi_reconnect_count\":%lu,"

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

    DEVICE_ID,

    GATEWAY_ID,

    ZONE_ID,

    SESSION_ID,

    (unsigned long)sequenceNumber,

    (unsigned long long)deviceTimestamp,

    (unsigned long)wifiReconnectCount,

    temperature,

    humidity,

    ax,

    ay,

    az,

    waterRaw,

    loadRaw,

    loadKg,

    dhtValid ? "true" : "false",

    mpuValid ? "true" : "false",

    hx711Valid ? "true" : "false",

    quality
  );

  if (
    payloadLength < 0 ||
    payloadLength >= sizeof(payload)
  ) {

    Serial.println("ERROR: JSON payload overflow.");

    return;
  }

  // ==================================================
  // HTTP POST
  // ==================================================

  HTTPClient http;

  http.setTimeout(5000);

  http.setReuse(false);

  if (!http.begin(API_URL)) {

    Serial.println("ERROR: Could not initialize HTTP.");

    return;
  }

  http.addHeader(
    "Content-Type",
    "application/json"
  );

  int httpCode = http.POST(
    (uint8_t*)payload,
    strlen(payload)
  );

  // ==================================================
  // SERIAL MONITOR
  // ==================================================

  Serial.println();

  Serial.println("========== TELEMETRY ==========");

  Serial.printf(
    "Sequence Number: %lu\n",
    (unsigned long)sequenceNumber
  );

  Serial.printf(
    "Temperature: %.2f C\n",
    temperature
  );

  Serial.printf(
    "Humidity: %.2f %%\n",
    humidity
  );

  Serial.printf(
    "Acceleration: %.3f %.3f %.3f\n",
    ax,
    ay,
    az
  );

  Serial.printf(
    "Water Raw: %d\n",
    waterRaw
  );

  Serial.printf(
    "Load Raw: %ld\n",
    loadRaw
  );

  Serial.printf(
    "Load Weight: %.3f kg %s\n",
    loadKg,
    loadCalibrated ? "" : "(NOT CALIBRATED)"
  );

  Serial.printf(
    "WiFi Reconnection Count: %lu\n",
    (unsigned long)wifiReconnectCount
  );

  Serial.printf(
    "Device Timestamp: %llu\n",
    (unsigned long long)deviceTimestamp
  );

  Serial.printf(
    "NTP Status: %s\n",
    ntpSynced ? "SYNCED" : "NOT SYNCED"
  );

  Serial.printf(
    "Quality: %s\n",
    quality
  );

  Serial.printf(
    "HTTP Status: %d\n",
    httpCode
  );

  // ==================================================
  // HTTP RESPONSE HANDLING
  // ==================================================

  if (httpCode == 201) {

    Serial.println("Data successfully saved!");

    Serial.print("API Response: ");

    Serial.println(http.getString());

    sequenceNumber++;

  }

  else if (httpCode > 0) {

    Serial.printf(
      "Server returned HTTP %d\n",
      httpCode
    );

    Serial.println(http.getString());

  }

  else {

    Serial.print("HTTP error: ");

    Serial.println(
      http.errorToString(httpCode)
    );
  }

  Serial.println("===============================");

  http.end();
}
