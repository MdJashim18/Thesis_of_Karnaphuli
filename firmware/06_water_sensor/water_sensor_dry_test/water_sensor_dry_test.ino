const int WATER_SENSOR_PIN = 34;
const int NUM_SAMPLES = 16;

int readAveragedADC() {
  long sum = 0;
  for (int i = 0; i < NUM_SAMPLES; i++) {
    sum += analogRead(WATER_SENSOR_PIN);
    delayMicroseconds(200);
  }
  return sum / NUM_SAMPLES;
}

int readAveragedMilliVolts() {
  long sum = 0;
  for (int i = 0; i < NUM_SAMPLES; i++) {
    sum += analogReadMilliVolts(WATER_SENSOR_PIN);
    delayMicroseconds(200);
  }
  return sum / NUM_SAMPLES;
}

void setup() {
  Serial.begin(115200);
  analogReadResolution(12);
  analogSetPinAttenuation(WATER_SENSOR_PIN, ADC_11db);

  Serial.println("Water Sensor Dry-State Test");
  Serial.println("ADC readings:");
}

void loop() {
  int adcValue = readAveragedADC();
  int voltageMilliVolts = readAveragedMilliVolts();

  Serial.print("ADC: ");
  Serial.print(adcValue);
  Serial.print(" | Voltage: ");
  Serial.print(voltageMilliVolts);
  Serial.println(" mV");

  delay(500);
}