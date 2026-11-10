
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
#include <string.h>

// ==================================================
// 1. WIFI AND API CONFIGURATION
// ==================================================

const char* WIFI_SSID = "Bachelor";
const char* WIFI_PASSWORD = "12344321";

// Check current PC IPv4 using ipconfig
const char* API_URL = "http://192.168.0.107:5000/telemetry";


// ==================================================
// 2. DEVICE CONFIGURATION
// ==================================================

const char* DEVICE_ID = "ESP32-GW-LAB-001";
const char* GATEWAY_ID = "gateway01";
const char* ZONE_ID = "LAB_PROTOTYPE";
const char* SESSION_ID = "SHM-TEST-001";


// ==================================================
// 3. SENSOR PINS
// ==================================================

#define DHT_PIN 4
#define DHT_TYPE DHT22

#define WATER_PIN 34

#define HX711_DOUT 18
#define HX711_SCK 19


// ==================================================
// 4. SYSTEM CONFIGURATION
// ==================================================

const unsigned long PUBLISH_INTERVAL = 1000;
const unsigned long DHT_INTERVAL = 2000;
const unsigned long WIFI_RETRY = 5000;

const bool DEBUG_LOAD = true;


// ==================================================
// 5. SENSOR OBJECTS
// ==================================================

DHT dht(DHT_PIN, DHT_TYPE);

Adafruit_MPU6050 mpu;

HX711 scale;

Preferences prefs;

bool mpuReady = false;


// ==================================================
// 6. LOAD CELL CALIBRATION VARIABLES
// ==================================================

// Calibration factor unit: raw counts per kg

long loadOffset = 0;

float loadScale = 0.0f;

bool loadCalibrated = false;

// Indicates whether tare has been completed.
// This is separate from loadOffset because a valid
// tare offset can theoretically be zero.

bool tareCompleted = false;


// ==================================================
// 7. RELIABILITY VARIABLES
// ==================================================

uint32_t sequenceNumber = 0;

uint32_t wifiReconnectCount = 0;

bool hasConnectedOnce = false;

bool ntpSynced = false;


// ==================================================
// 8. TIMER VARIABLES
// ==================================================

unsigned long lastPublish = 0;

unsigned long lastDHTRead = 0;

unsigned long lastWiFiAttempt = 0;


// ==================================================
// 9. SENSOR DATA
// ==================================================

float temperature = 0.0f;

float humidity = 0.0f;

bool dhtValid = false;


// ==================================================
// 10. LAST LOAD CELL DATA
// ==================================================

long lastLoadRaw = 0;

float lastLoadKg = 0.0f;

float lastLoadGram = 0.0f;

bool lastHX711Valid = false;


// ==================================================
// 11. DEVICE TIMESTAMP
// ==================================================

uint64_t getDeviceTimestampMs() {

    struct timeval tv;

    gettimeofday(&tv, nullptr);

    return (uint64_t)tv.tv_sec * 1000ULL
           + tv.tv_usec / 1000ULL;
}


bool clockIsSet() {

    return time(nullptr) >= 1700000000;
}


// ==================================================
// 12. WIFI CONNECTION
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
                "Wi-Fi Reconnection Count: %lu\n",
                (unsigned long)wifiReconnectCount
            );
        }

        hasConnectedOnce = true;

        Serial.println("Wi-Fi connected!");

        Serial.print("ESP32 IP: ");

        Serial.println(WiFi.localIP());

        Serial.print("API URL: ");

        Serial.println(API_URL);

        return true;
    }

    Serial.println("Wi-Fi connection failed.");

    return false;
}


// ==================================================
// 13. NTP TIME SYNCHRONIZATION
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

        if (clockIsSet()) {

            ntpSynced = true;

            time_t now = time(nullptr);

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
// 14. SAVE CALIBRATION TO ESP32 PREFERENCES
// ==================================================

void saveCalibration() {

    prefs.putLong("offset", loadOffset);

    prefs.putFloat("scale", loadScale);

    prefs.putBool("calibrated", loadCalibrated);

    prefs.putBool("tared", tareCompleted);

    Serial.println("[CAL] Calibration information saved.");
}


// ==================================================
// 15. LOAD CALIBRATION FROM ESP32 PREFERENCES
// ==================================================

void loadSavedCalibration() {

    loadOffset = prefs.getLong("offset", 0);

    loadScale = prefs.getFloat("scale", 0.0f);

    bool savedCalibration =
        prefs.getBool("calibrated", false);

    tareCompleted =
        prefs.getBool("tared", false);

    loadCalibrated =
        savedCalibration &&
        tareCompleted &&
        isfinite(loadScale) &&
        fabs(loadScale) > 0.001f;

    Serial.println();
    Serial.println("===== SAVED LOAD CELL CALIBRATION =====");

    Serial.printf(
        "Offset: %ld\n",
        loadOffset
    );

    Serial.printf(
        "Scale: %.3f raw/kg\n",
        loadScale
    );

    Serial.printf(
        "Tare completed: %s\n",
        tareCompleted ? "YES" : "NO"
    );

    Serial.printf(
        "Calibration: %s\n",
        loadCalibrated ? "YES" : "NO"
    );

    Serial.println("=======================================");
}


// ==================================================
// 16. PRINT CALIBRATION STATUS
// ==================================================

void showCalibration() {

    Serial.println();
    Serial.println("========== CURRENT CALIBRATION ==========");

    Serial.printf("Offset: %ld\n", loadOffset);

    Serial.printf(
        "Scale: %.3f raw/kg\n",
        loadScale
    );

    Serial.printf(
        "Tare: %s\n",
        tareCompleted ? "COMPLETED" : "NOT COMPLETED"
    );

    Serial.printf(
        "Calibration: %s\n",
        loadCalibrated ? "ACTIVE" : "INACTIVE"
    );

    Serial.println("=========================================");
}


// ==================================================
// 17. RESET CALIBRATION
// ==================================================

void resetCalibration() {

    loadOffset = 0;

    loadScale = 0.0f;

    loadCalibrated = false;

    tareCompleted = false;

    saveCalibration();

    Serial.println();
    Serial.println("[CAL] Calibration reset successfully.");
    Serial.println("[CAL] Please perform Tare again.");
}


// ==================================================
// 18. TARE LOAD CELL
// ==================================================

void tareLoadCell() {

    Serial.println();
    Serial.println("[CAL] Tare operation started.");

    Serial.println("[CAL] Keep the platform EMPTY.");

    delay(3000);

    if (!scale.wait_ready_timeout(3000)) {

        Serial.println("[CAL] ERROR: HX711 not ready.");

        return;
    }

    long newOffset = scale.read_average(30);

    loadOffset = newOffset;

    loadScale = 0.0f;

    loadCalibrated = false;

    tareCompleted = true;

    saveCalibration();

    Serial.println();
    Serial.println("========== TARE RESULT ==========");

    Serial.printf(
        "New Offset: %ld\n",
        loadOffset
    );

    Serial.println("Tare Status: SUCCESS");

    Serial.println("=================================");
}


// ==================================================
// 19. CALIBRATE LOAD CELL
// ==================================================

void calibrateLoadCell(float referenceGrams) {

    if (!tareCompleted) {

        Serial.println(
            "[CAL] ERROR: Tare first using command t."
        );

        return;
    }

    if (
        !isfinite(referenceGrams) ||
        referenceGrams <= 0.0f
    ) {

        Serial.println(
            "[CAL] ERROR: Invalid reference weight."
        );

        return;
    }

    Serial.println();

    Serial.printf(
        "[CAL] Place %.2f g reference weight.\n",
        referenceGrams
    );

    Serial.println(
        "[CAL] Keep the weight stable..."
    );

    delay(3000);

    if (!scale.wait_ready_timeout(3000)) {

        Serial.println(
            "[CAL] ERROR: HX711 not ready."
        );

        return;
    }

    // Read average raw value

    long raw = scale.read_average(30);

    // Calculate net raw

    long netRaw = raw - loadOffset;

    float referenceKg =
        referenceGrams / 1000.0f;

    if (labs(netRaw) < 100) {

        Serial.println(
            "[CAL] ERROR: Net raw value is too small."
        );

        Serial.println(
            "[CAL] Check load cell wiring and reference weight."
        );

        return;
    }

    // Calculate calibration factor

    float newScale =
        (float)netRaw / referenceKg;

    if (
        !isfinite(newScale) ||
        fabs(newScale) < 0.001f
    ) {

        Serial.println(
            "[CAL] ERROR: Invalid calibration factor."
        );

        return;
    }

    // Activate calibration

    loadScale = newScale;

    loadCalibrated = true;

    // Save to Preferences

    saveCalibration();

    // Calculate calibration result

    float calculatedKg =
        (float)netRaw / loadScale;

    float calculatedGram =
        calculatedKg * 1000.0f;

    Serial.println();

    Serial.println("========== CALIBRATION SUCCESS ==========");

    Serial.printf(
        "Reference Weight: %.2f g\n",
        referenceGrams
    );

    Serial.printf(
        "Raw Reading: %ld\n",
        raw
    );

    Serial.printf(
        "Tare Offset: %ld\n",
        loadOffset
    );

    Serial.printf(
        "Net Raw: %ld\n",
        netRaw
    );

    Serial.printf(
        "Calibration Factor: %.3f raw/kg\n",
        loadScale
    );

    Serial.printf(
        "Calibration Check: %.2f g\n",
        calculatedGram
    );

    Serial.println("Calibration Status: ACTIVE");

    Serial.println("==========================================");
}


// ==================================================
// 20. SERIAL COMMAND HANDLER
//
// t      = Tare
// c100   = Calibrate using 100g
// c500   = Calibrate using 500g
// s      = Show calibration
// r      = Reset calibration
// ================================================

void handleSerial() {

    if (!Serial.available()) return;

    String cmd = Serial.readStringUntil('\n');

    cmd.trim();

    if (cmd.length() == 0) return;

    if (cmd == "s") {

        showCalibration();

        return;
    }

    if (cmd == "r") {

        resetCalibration();

        return;
    }

    if (!scale.wait_ready_timeout(2000)) {

        Serial.println(
            "[HX711] ERROR: Sensor not ready."
        );

        return;
    }

    if (cmd == "t") {

        tareLoadCell();

        return;
    }

    if (cmd.startsWith("c")) {

        float referenceGrams =
            cmd.substring(1).toFloat();

        calibrateLoadCell(referenceGrams);

        return;
    }

    Serial.println();
    Serial.println("Available Commands:");

    Serial.println("t     = Tare");

    Serial.println("c100  = Calibrate using 100g");

    Serial.println("c500  = Calibrate using 500g");

    Serial.println("s     = Show calibration");

    Serial.println("r     = Reset calibration");
}


// ==================================================
// 21. READ LOAD CELL
// ==================================================

bool readLoadCell(
    long &rawValue,
    float &weightKg,
    float &weightGram
) {

    rawValue = 0;

    weightKg = 0.0f;

    weightGram = 0.0f;

    // Check HX711 readiness

    if (!scale.wait_ready_timeout(500)) {

        return false;
    }

    // Read raw sensor value

    rawValue = scale.read_average(5);

    // Calibration inactive

    if (!loadCalibrated) {

        return true;
    }

    // Check calibration factor

    if (
        !isfinite(loadScale) ||
        fabs(loadScale) < 0.001f
    ) {

        loadCalibrated = false;

        return true;
    }

    // Calculate net raw value

    long netRaw = rawValue - loadOffset;

    // Convert raw counts into kg

    weightKg =
        (float)netRaw / loadScale;

    // Convert kg into grams

    weightGram =
        weightKg * 1000.0f;

    // Validate calculation

    if (
        !isfinite(weightKg) ||
        !isfinite(weightGram)
    ) {

        weightKg = 0.0f;

        weightGram = 0.0f;

        return false;
    }

    return true;
}


// ==================================================
// 22. LOAD CELL DEBUG
// ==================================================

void debugLoadCell() {

    Serial.println();

    Serial.println("========== LOAD CELL DEBUG ==========");

    Serial.printf(
        "HX711 Ready: %s\n",
        lastHX711Valid ? "YES" : "NO"
    );

    Serial.printf(
        "Tare Status: %s\n",
        tareCompleted ? "YES" : "NO"
    );

    Serial.printf(
        "Calibration Status: %s\n",
        loadCalibrated ? "YES" : "NO"
    );

    Serial.printf(
        "Load Offset: %ld\n",
        loadOffset
    );

    Serial.printf(
        "Load Scale: %.3f raw/kg\n",
        loadScale
    );

    Serial.printf(
        "Raw Reading: %ld\n",
        lastLoadRaw
    );

    Serial.printf(
        "Net Raw: %ld\n",
        lastLoadRaw - loadOffset
    );

    Serial.printf(
        "Calculated Weight: %.5f kg\n",
        lastLoadKg
    );

    Serial.printf(
        "Calculated Weight: %.2f gram\n",
        lastLoadGram
    );

    Serial.println("=====================================");
}


// ==================================================
// 23. SETUP
// ==================================================

void setup() {

    Serial.begin(115200);

    delay(1000);

    Serial.println();

    Serial.println("======================================");

    Serial.println("KARNAPHULI TUNNEL SHM");

    Serial.println("ESP32 HTTP TELEMETRY SYSTEM");

    Serial.println("LOAD CELL CALIBRATION VERSION 2");

    Serial.println("======================================");

    Serial.setTimeout(100);

    // ----------------------------------------------
    // PREFERENCES
    // ----------------------------------------------

    if (!prefs.begin("loadcal", false)) {

        Serial.println(
            "[ERROR] Could not initialize Preferences."
        );
    }

    loadSavedCalibration();


    // ----------------------------------------------
    // DHT22
    // ----------------------------------------------

    dht.begin();

    Serial.println("[INIT] DHT22 initialized.");


    // ----------------------------------------------
    // MPU6050
    // ----------------------------------------------

    Wire.begin(21, 22);

    if (mpu.begin()) {

        mpuReady = true;

        Serial.println("[INIT] MPU6050 detected.");

    } else {

        Serial.println(
            "[WARNING] MPU6050 not detected."
        );
    }


    // ----------------------------------------------
    // HX711
    // ----------------------------------------------

    scale.begin(
        HX711_DOUT,
        HX711_SCK
    );

    if (scale.wait_ready_timeout(3000)) {

        Serial.println("[INIT] HX711 detected.");

    } else {

        Serial.println(
            "[WARNING] HX711 not ready."
        );
    }


    // ----------------------------------------------
    // WIFI
    // ----------------------------------------------

    if (connectWiFi()) {

        synchronizeTime();
    }


    // ----------------------------------------------
    // INITIAL DHT READING
    // ----------------------------------------------

    float t = dht.readTemperature();

    float h = dht.readHumidity();

    if (
        !isnan(t) &&
        !isnan(h)
    ) {

        temperature = t;

        humidity = h;

        dhtValid = true;

        lastDHTRead = millis();

    } else {

        dhtValid = false;

        temperature = 0.0f;

        humidity = 0.0f;
    }


    // ----------------------------------------------
    // INITIALIZATION COMPLETE
    // ----------------------------------------------

    Serial.println();

    Serial.println("System initialization completed.");

    Serial.println();

    Serial.println("LOAD CELL COMMANDS:");

    Serial.println("t = Tare");

    Serial.println("c100 = Calibrate using 100g");

    Serial.println("c500 = Calibrate using 500g");

    Serial.println("s = Show calibration");

    Serial.println("r = Reset calibration");

    Serial.println();

    Serial.println("Waiting for telemetry...");

    lastPublish = millis();
}


// ==================================================
// 24. MAIN LOOP
// ==================================================

void loop() {

    // ----------------------------------------------
    // SERIAL COMMANDS
    // ----------------------------------------------

    handleSerial();

    unsigned long now = millis();


    // ----------------------------------------------
    // WIFI RECONNECTION
    // ----------------------------------------------

    if (WiFi.status() != WL_CONNECTED) {

        if (now - lastWiFiAttempt >= WIFI_RETRY) {

            lastWiFiAttempt = now;

            if (connectWiFi()) {

                synchronizeTime();
            }
        }

        return;
    }


    // ----------------------------------------------
    // NTP STATUS
    // ----------------------------------------------

    if (!ntpSynced && clockIsSet()) {

        ntpSynced = true;

        Serial.println("[NTP] Clock synchronized.");
    }


    // ----------------------------------------------
    // PUBLISH INTERVAL
    // ----------------------------------------------

    if (now - lastPublish < PUBLISH_INTERVAL) {

        return;
    }

    lastPublish = now;


    // ==================================================
    // DHT22
    // ==================================================

    if (now - lastDHTRead >= DHT_INTERVAL) {

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

        } else {

            dhtValid = false;

            Serial.println(
                "[DHT] WARNING: Reading failed."
            );
        }
    }


    // ==================================================
    // MPU6050
    // ==================================================

    float ax = 0.0f;

    float ay = 0.0f;

    float az = 0.0f;

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

        float x = accel.acceleration.x;

        float y = accel.acceleration.y;

        float z = accel.acceleration.z;

        if (
            isfinite(x) &&
            isfinite(y) &&
            isfinite(z)
        ) {

            ax = x;

            ay = y;

            az = z;

            mpuValid = true;
        }
    }


    // ==================================================
    // WATER SENSOR
    // ==================================================

    int waterRaw = analogRead(WATER_PIN);


    // ==================================================
    // HX711 LOAD CELL
    // ==================================================

    lastHX711Valid = readLoadCell(
        lastLoadRaw,
        lastLoadKg,
        lastLoadGram
    );

    bool calibratedNow = (
        lastHX711Valid &&
        loadCalibrated
    );


    // ==================================================
    // LOAD CELL DEBUG
    // ==================================================

    if (DEBUG_LOAD) {

        debugLoadCell();
    }


    // ==================================================
    // QUALITY FLAG
    // ==================================================

    const char* quality;

    if (
        !dhtValid ||
        !mpuValid ||
        !lastHX711Valid
    ) {

        quality = "degraded";
    }

    else if (!calibratedNow) {

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

    char payload[1400];

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
        "\"load_kg\":%.5f,"
        "\"load_gram\":%.2f,"

        "\"load_calibrated\":%s,"

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

        lastLoadRaw,
        lastLoadKg,
        lastLoadGram,

        calibratedNow ? "true" : "false",

        dhtValid ? "true" : "false",

        mpuValid ? "true" : "false",

        lastHX711Valid ? "true" : "false",

        quality
    );


    // ----------------------------------------------
    // JSON VALIDATION
    // ----------------------------------------------

    if (
        payloadLength < 0 ||
        payloadLength >= (int)sizeof(payload)
    ) {

        Serial.println(
            "[ERROR] JSON payload overflow."
        );

        return;
    }


    // ==================================================
    // HTTP POST
    // ==================================================

    HTTPClient http;

    http.setTimeout(5000);

    http.setReuse(false);

    if (!http.begin(API_URL)) {

        Serial.println(
            "[HTTP] ERROR: Could not initialize HTTP."
        );

        return;
    }

    http.addHeader(
        "Content-Type",
        "application/json"
    );

    int httpCode = http.POST(
        (uint8_t*)payload,
        payloadLength
    );


    // ==================================================
    // TELEMETRY SERIAL OUTPUT
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
        "Acceleration: %.3f, %.3f, %.3f\n",
        ax, ay, az
    );

    Serial.printf(
        "Water Raw: %d\n",
        waterRaw
    );

    Serial.printf(
        "Load Raw: %ld\n",
        lastLoadRaw
    );

    Serial.printf(
        "Load Offset: %ld\n",
        loadOffset
    );

    Serial.printf(
        "Load Scale: %.3f raw/kg\n",
        loadScale
    );

    Serial.printf(
        "Load Weight: %.5f kg\n",
        lastLoadKg
    );

    Serial.printf(
        "Load Weight: %.2f gram\n",
        lastLoadGram
    );

    Serial.printf(
        "Load Calibration: %s\n",
        calibratedNow ? "YES" : "NO"
    );

    Serial.printf(
        "HX711 Status: %s\n",
        lastHX711Valid ? "READY" : "NOT READY"
    );

    Serial.printf(
        "WiFi Reconnection Count: %lu\n",
        (unsigned long)wifiReconnectCount
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
    // HTTP RESPONSE
    // ==================================================

    if (httpCode == 200) {

        Serial.println(
            "[HTTP] Telemetry successfully stored!"
        );

        String response = http.getString();

        Serial.print("API Response: ");

        Serial.println(response);

        sequenceNumber++;
    }

    else if (httpCode > 0) {

        Serial.printf(
            "[HTTP] Server returned HTTP %d\n",
            httpCode
        );

        Serial.println(http.getString());
    }

    else {

        Serial.print("[HTTP] Error: ");

        Serial.println(
            http.errorToString(httpCode)
        );
    }

    Serial.println("===============================");

    http.end();
}
