
#include "HX711.h"
#include <math.h>

#define HX711_DOUT 18
#define HX711_SCK  19

HX711 scale;

// Calibration weight
const float CAL_WEIGHT_G = 100.0;

// Validation weight
const float VAL_WEIGHT_G = 500.0;

const int NUM_TRIALS = 3;
const int SAMPLES    = 20;

float calibrationFactor = 1.0;

float measured[NUM_TRIALS];
float errorsG[NUM_TRIALS];
float errorsPct[NUM_TRIALS];

void waitForEnter() {
  while (Serial.available()) Serial.read();

  while (!Serial.available()) {
    delay(10);
  }

  delay(50);

  while (Serial.available()) Serial.read();
}

void halt(const char *msg) {
  Serial.println(msg);

  while (true) {
    delay(1000);
  }
}

void waitUntilReady(uint32_t timeoutMs, const char *msg) {
  if (!scale.wait_ready_timeout(timeoutMs)) {
    halt(msg);
  }
}

void setup() {
  Serial.begin(115200);
  delay(1500);

  Serial.println();
  Serial.println("=== HX711 Calibration & Validation ===");

  scale.begin(HX711_DOUT, HX711_SCK);

  waitUntilReady(5000, "ERROR: HX711 NOT READY. Check wiring.");

  Serial.println("HX711 ready.");

  // ---------- Step 1: Tare ----------

  Serial.println("Remove all weight. Keep platform still.");
  Serial.println("Press Enter to tare.");

  waitForEnter();

  scale.set_scale();
  scale.tare(SAMPLES);

  Serial.println("Tare complete.");

  // ---------- Step 2: Calibration ----------

  Serial.print("Place exactly ");
  Serial.print(CAL_WEIGHT_G, 1);
  Serial.println(" g. Wait until stable, then press Enter.");

  waitForEnter();

  waitUntilReady(3000, "ERROR: HX711 not ready.");

  double netRaw = scale.get_value(SAMPLES);

  Serial.print("Calibration net raw: ");
  Serial.println(netRaw, 2);

  if (fabs(netRaw) < 100.0) {
    halt("ERROR: Signal too small. Check load cell mounting and wiring.");
  }

  calibrationFactor = (float)(netRaw / CAL_WEIGHT_G);

  scale.set_scale(calibrationFactor);

  Serial.print("Calibration factor: ");
  Serial.println(calibrationFactor, 6);

  Serial.print("Calibration check (g): ");
  Serial.println(scale.get_units(SAMPLES), 2);

  Serial.println();
  Serial.println("=== 500 g Validation ===");

  Serial.print("Weight to use for validation: ");
  Serial.print(VAL_WEIGHT_G, 1);
  Serial.println(" g");

  Serial.println("Three validation trials will be performed.");
}

void loop() {

  static int trial = 0;

  if (trial >= NUM_TRIALS) {
    printSummary();

    while (true) {
      delay(1000);
    }
  }

  Serial.println();

  Serial.print("Trial ");
  Serial.print(trial + 1);

  Serial.println(": Empty the platform, then press Enter to tare.");

  waitForEnter();

  if (!scale.wait_ready_timeout(3000)) {
    Serial.println("ERROR: HX711 not ready. Retrying...");
    delay(500);
    return;
  }

  scale.tare(SAMPLES);

  Serial.print("Place ");
  Serial.print(VAL_WEIGHT_G, 1);

  Serial.println(" g, wait until stable, then press Enter.");

  waitForEnter();

  if (!scale.wait_ready_timeout(3000)) {
    Serial.println("ERROR: HX711 not ready. Retrying trial...");
    delay(500);
    return;
  }

  float w = scale.get_units(SAMPLES);

  float err = w - VAL_WEIGHT_G;

  float pct = fabs(err) / VAL_WEIGHT_G * 100.0;

  measured[trial]  = w;
  errorsG[trial]   = err;
  errorsPct[trial] = pct;

  Serial.print("Known (g): ");
  Serial.print(VAL_WEIGHT_G, 2);

  Serial.print(" | Measured (g): ");
  Serial.print(w, 2);

  Serial.print(" | Error (g): ");
  Serial.print(err, 2);

  Serial.print(" | Error (%): ");
  Serial.println(pct, 2);

  trial++;
}

// ---------- Step 3: Summary ----------

void printSummary() {

  float sum = 0;
  float sumErrPct = 0;

  for (int i = 0; i < NUM_TRIALS; i++) {

    sum += measured[i];

    sumErrPct += errorsPct[i];
  }

  float mean = sum / NUM_TRIALS;

  float var = 0;

  for (int i = 0; i < NUM_TRIALS; i++) {

    float d = measured[i] - mean;

    var += d * d;
  }

  float sd = (NUM_TRIALS > 1)
             ? sqrt(var / (NUM_TRIALS - 1))
             : 0;

  Serial.println();

  Serial.println("=== 500 g Validation Summary ===");

  Serial.print("Calibration factor: ");
  Serial.println(calibrationFactor, 6);

  Serial.print("Calibration weight (g): ");
  Serial.println(CAL_WEIGHT_G, 2);

  Serial.print("Validation weight (g): ");
  Serial.println(VAL_WEIGHT_G, 2);

  Serial.print("Mean measured (g): ");
  Serial.println(mean, 3);

  Serial.print("Std dev (g): ");
  Serial.println(sd, 3);

  Serial.print("Mean error (g): ");
  Serial.println(mean - VAL_WEIGHT_G, 3);

  Serial.print("Mean abs error (%): ");
  Serial.println(sumErrPct / NUM_TRIALS, 3);

  Serial.println("500 g validation completed.");
  Serial.println("Record these results.");
}
