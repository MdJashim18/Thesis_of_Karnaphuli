
unsigned long start_time;

void setup() {
  Serial.begin(115200);
  start_time = millis();
}

void loop() {
  unsigned long uptime = millis() - start_time;

  Serial.print("Uptime: ");
  Serial.print(uptime);
  Serial.println(" ms");

  delay(1000);
}
