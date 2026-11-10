
import json
from pathlib import Path
from collections import Counter, defaultdict

PROJECT = Path(r"D:\karnaphuli-shm-month2")
FILE = PROJECT / "data" / "raw" / "continuous_24h.jsonl"

records = []

with open(FILE, encoding="utf-8") as f:
    for line in f:
        if line.strip():
            records.append(json.loads(line))

print("=" * 65)
print("MONTH 2 - DEEP DATASET ANALYSIS")
print("=" * 65)

# 1. Device timestamp
zero_timestamps = []
invalid_timestamps = []

for i, r in enumerate(records, 1):
    value = r.get("device_timestamp_ms")

    try:
        if value is None or float(value) <= 0:
            zero_timestamps.append((i, value, r.get("received_at")))
    except (ValueError, TypeError):
        invalid_timestamps.append((i, value))

print("\n[1] DEVICE TIMESTAMP")
print("Zero/missing timestamps:", len(zero_timestamps))
print("Invalid timestamps:", len(invalid_timestamps))

print("First 10 zero/missing examples:")
for item in zero_timestamps[:10]:
    print(item)

# 2. Boot ID
boot_counts = Counter(
    r.get("boot_id", "MISSING")
    for r in records
)

print("\n[2] BOOT ID DISTRIBUTION")
for boot, count in boot_counts.most_common():
    print(f"{boot}: {count}")

# 3. Sequence analysis by boot ID
sequence_groups = defaultdict(list)

for r in records:
    boot = r.get("boot_id", "MISSING")
    seq = r.get("sequence_number")

    if isinstance(seq, int):
        sequence_groups[boot].append(seq)

print("\n[3] SEQUENCE BY BOOT ID")

for boot, seqs in sequence_groups.items():
    print(
        boot,
        "| records:", len(seqs),
        "| unique:", len(set(seqs)),
        "| min:", min(seqs),
        "| max:", max(seqs),
        "| duplicates:", len(seqs) - len(set(seqs))
    )

# 4. Exact duplicate JSON records
serialized = [
    json.dumps(r, sort_keys=True)
    for r in records
]

exact_duplicates = len(serialized) - len(set(serialized))

print("\n[4] EXACT DUPLICATES")
print("Exact duplicate records:", exact_duplicates)

# 5. Partial quality reasons
partial_records = [
    r for r in records
    if r.get("quality_flag") == "partial"
]

print("\n[5] PARTIAL RECORD ANALYSIS")
print("Partial records:", len(partial_records))

for field in [
    "dht_valid",
    "mpu_valid",
    "hx711_valid",
    "load_calibrated"
]:
    true_count = sum(
        r.get(field) is True for r in partial_records
    )
    false_count = sum(
        r.get(field) is False for r in partial_records
    )
    missing_count = sum(
        field not in r for r in partial_records
    )

    print(
        field,
        "| true:", true_count,
        "| false:", false_count,
        "| missing:", missing_count
    )

# 6. Latency validity
latency_counts = Counter(
    str(r.get("latency_valid", "MISSING"))
    for r in records
)

print("\n[6] LATENCY VALIDITY")
for key, count in latency_counts.items():
    print(key, count)

# 7. Reconnect counter by boot ID
print("\n[7] RECONNECTION BY BOOT ID")

reconnect_groups = defaultdict(list)

for r in records:
    boot = r.get("boot_id", "MISSING")
    count = r.get("wifi_reconnect_count")

    if isinstance(count, int):
        reconnect_groups[boot].append(count)

for boot, values in reconnect_groups.items():
    print(
        boot,
        "| records:", len(values),
        "| first:", values[0],
        "| last:", values[-1],
        "| maximum:", max(values)
    )

print("\nAnalysis completed.")
