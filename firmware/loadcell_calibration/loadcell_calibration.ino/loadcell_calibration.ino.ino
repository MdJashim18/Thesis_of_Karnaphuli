
#include "HX711.h"
#include <math.h>

#define HX711_DOUT 18
#define HX711_SCK  19

HX711 scale;

// Calibration weight
const float CAL_WEIGHT_G = 100.0;

// Validation weights
const float VAL_WEIGHTS[] = {
  100.0, 200.0, 500.0, 1000.0
};

const int NUM_WEIGHTS = 4;
const int NUM_TRIALS = 3;
const int SAMPLES = 20;

float calibrationFactor = 1.0;

float measured[NUM_WEIGHTS][NUM_TRIALS];
float errorsG[NUM_WEIGHTS][NUM_TRIALS];
float errorsPct[NUM_WEIGHTS][NUM_TRIALS];

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

  Serial.println();
  Serial.println("=== STEP 1: TARE ===");

  Serial.println("Remove all weight. Keep platform still.");
  Serial.println("Press Enter to tare.");

  waitForEnter();

  scale.set_scale();
  scale.tare(SAMPLES);

  Serial.println("Tare complete.");

  // ---------- Step 2: Calibration ----------

  Serial.println();
  Serial.println("=== STEP 2: CALIBRATION ===");

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
  Serial.println("=== VALIDATION STARTED ===");

  Serial.println("Validation weights: 100g, 200g, 500g, 1000g");
  Serial.println("Three trials for each weight.");
}

void loop() {

  static int weightIndex = 0;
  static int trial = 0;

  if (weightIndex >= NUM_WEIGHTS) {
    printSummary();

    while (true) {
      delay(1000);
    }
  }

  float targetWeight = VAL_WEIGHTS[weightIndex];

  Serial.println();
  Serial.println("--------------------------------");

  Serial.print("Validation Weight: ");
  Serial.print(targetWeight, 1);
  Serial.println(" g");

  Serial.print("Trial ");
  Serial.print(trial + 1);
  Serial.print("/");
  Serial.println(NUM_TRIALS);

  // ---------- Tare ----------

  Serial.println("Remove all weight, then press Enter to tare.");

  waitForEnter();

  if (!scale.wait_ready_timeout(3000)) {
    Serial.println("ERROR: HX711 not ready. Retrying...");
    delay(500);
    return;
  }

  scale.tare(SAMPLES);

  Serial.println("Tare complete.");

  // ---------- Measurement ----------

  Serial.print("Place ");
  Serial.print(targetWeight, 1);
  Serial.println(" g. Wait until stable, then press Enter.");

  waitForEnter();

  if (!scale.wait_ready_timeout(3000)) {
    Serial.println("ERROR: HX711 not ready. Retrying trial...");
    delay(500);
    return;
  }

  float w = scale.get_units(SAMPLES);

  float err = w - targetWeight;

  float pct = fabs(err) / targetWeight * 100.0;

  measured[weightIndex][trial] = w;
  errorsG[weightIndex][trial] = err;
  errorsPct[weightIndex][trial] = pct;

  // ---------- Display Result ----------

  Serial.println();
  Serial.println("Trial Result:");

  Serial.print("Known (g): ");
  Serial.print(targetWeight, 2);

  Serial.print(" | Measured (g): ");
  Serial.print(w, 2);

  Serial.print(" | Error (g): ");
  Serial.print(err, 2);

  Serial.print(" | Error (%): ");
  Serial.println(pct, 2);

  trial++;

  if (trial >= NUM_TRIALS) {
    trial = 0;
    weightIndex++;

    Serial.println();
    Serial.println("All trials for this weight completed.");
  }
}

// ---------- Step 3: Summary ----------

void printSummary() {

  Serial.println();
  Serial.println("====================================");
  Serial.println(" FOUR-WEIGHT VALIDATION SUMMARY");
  Serial.println("====================================");

  Serial.print("Calibration factor: ");
  Serial.println(calibrationFactor, 6);

  Serial.print("Calibration weight (g): ");
  Serial.println(CAL_WEIGHT_G, 2);

  for (int j = 0; j < NUM_WEIGHTS; j++) {

    float target = VAL_WEIGHTS[j];

    float sum = 0;
    float sumErrPct = 0;

    for (int i = 0; i < NUM_TRIALS; i++) {
      sum += measured[j][i];
      sumErrPct += errorsPct[j][i];
    }

    float mean = sum / NUM_TRIALS;

    float variance = 0;

    for (int i = 0; i < NUM_TRIALS; i++) {
      float d = measured[j][i] - mean;
      variance += d * d;
    }

    float sd = sqrt(variance / (NUM_TRIALS - 1));

    float meanError = mean - target;

    float meanAbsError = sumErrPct / NUM_TRIALS;

    Serial.println();
    Serial.println("------------------------------------");

    Serial.print("Validation Weight: ");
    Serial.print(target, 2);
    Serial.println(" g");

    Serial.println("Individual Trials:");

    for (int i = 0; i < NUM_TRIALS; i++) {

      Serial.print("Trial ");
      Serial.print(i + 1);

      Serial.print(" | Measured: ");
      Serial.print(measured[j][i], 3);

      Serial.print(" g | Error: ");
      Serial.print(errorsG[j][i], 3);

      Serial.print(" g | Error: ");
      Serial.print(errorsPct[j][i], 3);

      Serial.println("%");
    }

    Serial.print("Mean measured (g): ");
    Serial.println(mean, 3);

    Serial.print("Std dev (g): ");
    Serial.println(sd, 3);

    Serial.print("Mean error (g): ");
    Serial.println(meanError, 3);

    Serial.print("Mean abs error (%): ");
    Serial.println(meanAbsError, 3);
  }

  Serial.println();
  Serial.println("====================================");
  Serial.println("ALL VALIDATION TESTS COMPLETED");
  Serial.println("====================================");
}
