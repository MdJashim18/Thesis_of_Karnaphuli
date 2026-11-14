
#include <DHT.h>
#include <math.h>

#define DHTPIN 4
#define DHTTYPE DHT22

DHT dht(DHTPIN, DHTTYPE);

const int TOTAL_READINGS = 100;
const unsigned long INTERVAL = 2000;

int readingCount = 0;
int invalidCount = 0;

void setup() {
  Serial.begin(115200);
  dht.begin();

  delay(2000);

  // CSV header
  Serial.println("timestamp,temperature,humidity");
}

void loop() {
  if (readingCount >= TOTAL_READINGS) {
    if (readingCount == TOTAL_READINGS) {
      Serial.print("# Invalid readings: ");
      Serial.println(invalidCount);
      readingCount++;
    }
    return;
  }

  unsigned long timestamp = readingCount * 2UL;

  float temperature = dht.readTemperature();
  float humidity = dht.readHumidity();

  bool invalid = isnan(temperature) || isnan(humidity);

  if (invalid) {
    invalidCount++;
  }

  Serial.print(timestamp);
  Serial.print(",");

  if (isnan(temperature)) {
    Serial.print("NaN");
  } else {
    Serial.print(temperature, 1);
  }

  Serial.print(",");

  if (isnan(humidity)) {
    Serial.println("NaN");
  } else {
    Serial.println(humidity, 1);
  }

  readingCount++;
  delay(INTERVAL);
}
