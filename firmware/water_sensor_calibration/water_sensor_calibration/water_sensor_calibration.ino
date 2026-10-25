
const int WATER_SENSOR_PIN = 34;
const int NUM_READINGS = 20;

void setup() {
  Serial.begin(115200);
  analogReadResolution(12);
  Serial.setTimeout(1000);

  Serial.println("Water Sensor Calibration");
  Serial.println("Enter level in cm: 0, 2, 5, 8, or 10");
  Serial.println("level_cm,sample,adc,reported_mV");
}

void loop() {
  if (Serial.available() > 0) {
    String input = Serial.readStringUntil('\n');
    input.trim();

    float level = input.toFloat();

    if (input != "0" && input != "2" &&
        input != "5" && input != "8" &&
        input != "10") {
      Serial.println("Invalid level. Enter 0, 2, 5, 8, or 10.");
      return;
    }

    Serial.println("Starting measurement...");
    delay(1000);

    for (int i = 1; i <= NUM_READINGS; i++) {
      int adc = analogRead(WATER_SENSOR_PIN);
      int mV = analogReadMilliVolts(WATER_SENSOR_PIN);

      Serial.print(level, 0);
      Serial.print(",");
      Serial.print(i);
      Serial.print(",");
      Serial.print(adc);
      Serial.print(",");
      Serial.println(mV);

      delay(500);
    }

    Serial.println("Measurement complete.");
    Serial.println("Enter the next water level.");
  }
}
