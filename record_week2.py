import json
import time
import serial
from pathlib import Path

PORT = "COM5"       # Arduino IDE-তে যে COM port দেখায়, সেটি দাও
BAUD = 115200
DURATION = 30 * 60  # 30 minutes

output = Path("data/raw/week2_test.jsonl")
output.parent.mkdir(parents=True, exist_ok=True)

count = 0
start = time.monotonic()

try:
    with serial.Serial(PORT, BAUD, timeout=2) as ser:
        time.sleep(2)
        ser.reset_input_buffer()

        print("Recording started. Keep ESP32 powered.")
        with output.open("w", encoding="utf-8") as f:
            while time.monotonic() - start < DURATION:
                raw = ser.readline().decode(
                    "utf-8", errors="replace"
                ).strip()

                if not raw:
                    continue

                try:
                    record = json.loads(raw)
                except json.JSONDecodeError:
                    print("Skipped non-JSON output:", raw)
                    continue

                f.write(json.dumps(record) + "\n")
                f.flush()
                count += 1

                if count % 30 == 0:
                    elapsed = int(time.monotonic() - start)
                    print(
                        f"Elapsed: {elapsed}s | "
                        f"Records saved: {count}"
                    )

    print(f"Finished. Saved {count} records to {output}")

except serial.SerialException as e:
    print("Serial connection error:", e)
    print("Check the COM port and close Arduino Serial Monitor.")