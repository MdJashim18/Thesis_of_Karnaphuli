import json
import statistics
from pathlib import Path
from datetime import datetime

BASE = Path(__file__).resolve().parent.parent

DATA_FILE = BASE / "data/raw/continuous_24h.jsonl"
RELIABILITY_FILE = BASE / "data/raw/reliability_log.jsonl"

# Firmware-এর প্রকৃত sampling interval বসাবে।
INTERVAL_SECONDS = 1

def load_jsonl(path):
    records = []

    with open(path, "r", encoding="utf-8") as f:
        for line in f:
            if line.strip():
                try:
                    records.append(json.loads(line))
                except json.JSONDecodeError:
                    print("Invalid JSON:", line[:100])

    return records


data = load_jsonl(DATA_FILE)
reliability = load_jsonl(RELIABILITY_FILE)

if not data:
    raise ValueError("No telemetry data found!")

timestamps = [
    datetime.fromisoformat(r["received_at"])
    for r in data
]

start = min(timestamps)
end = max(timestamps)

duration = (end - start).total_seconds()

expected = int(duration / INTERVAL_SECONDS) + 1

received = len(data)

missing = max(0, expected - received)

missing_rate = (
    missing / expected * 100
    if expected else 0
)

valid_latency = [
    r["latency_ms"]
    for r in reliability
    if r.get("latency_valid") is True
    and isinstance(r.get("latency_ms"), (int, float))
]

avg_latency = (
    statistics.mean(valid_latency)
    if valid_latency else None
)

reconnections = 0

previous = None

for r in reliability:
    current = r.get("wifi_reconnect_count")

    if current is None:
        continue

    if previous is not None and current > previous:
        reconnections += current - previous

    previous = current

print("\n===== DAY 27 REPORT =====")

print("Start:", start)
print("End:", end)
print("Duration:", duration, "seconds")

print("Expected:", expected)
print("Received:", received)
print("Missing:", missing)
print("Missing Rate:", round(missing_rate, 2), "%")

print("Valid Latency Samples:", len(valid_latency))
print("Average Latency:", avg_latency, "ms")

print("Reconnection Events:", reconnections)

print("=========================")