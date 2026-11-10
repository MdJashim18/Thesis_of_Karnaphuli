
import json
from pathlib import Path
from collections import Counter

PROJECT = Path(r"D:\karnaphuli-shm-month2")
FILE = PROJECT / "data" / "raw" / "continuous_24h.jsonl"

with open(FILE, encoding="utf-8") as f:
    records = [
        json.loads(line)
        for line in f
        if line.strip()
    ]

print("=" * 70)
print("MONTH 2 - DATASET TRANSITION INSPECTION")
print("=" * 70)

# 1. Find boot_id transition
print("\n[1] BOOT ID TRANSITIONS")

previous = object()

for i, r in enumerate(records):
    current = r.get("boot_id", "MISSING")

    if current != previous:
        print(
            f"Record {i+1}: boot_id={current}, "
            f"sequence={r.get('sequence_number')}, "
            f"received_at={r.get('received_at')}"
        )
        previous = current

# 2. Calibration transitions
print("\n[2] LOAD CALIBRATION TRANSITIONS")

previous = object()

for i, r in enumerate(records):
    current = r.get("load_calibrated", "MISSING")

    if current != previous:
        print(
            f"Record {i+1}: load_calibrated={current}, "
            f"load_kg={r.get('load_kg')}, "
            f"quality={r.get('quality_flag')}, "
            f"received_at={r.get('received_at')}"
        )
        previous = current

# 3. Degraded records
print("\n[3] DEGRADED RECORDS")

degraded = [
    (i, r)
    for i, r in enumerate(records, 1)
    if r.get("quality_flag") == "degraded"
]

print("Total degraded:", len(degraded))

for i, r in degraded:
    print("\nRecord:", i)
    print(json.dumps(r, indent=2))

# 4. Zero timestamps
print("\n[4] ZERO DEVICE TIMESTAMP RECORDS")

zero_indices = [
    i for i, r in enumerate(records)
    if r.get("device_timestamp_ms") in (0, None)
]

print("Total:", len(zero_indices))

for i in zero_indices[:15]:
    print("\nRecord:", i+1)
    print("Previous:", records[i-1] if i > 0 else None)
    print("Current:", records[i])
    print("Next:", records[i+1] if i+1 < len(records) else None)

# 5. Sequence resets in file order
print("\n[5] SEQUENCE RESETS")

resets = []

for i in range(1, len(records)):
    prev = records[i-1]
    curr = records[i]

    prev_seq = prev.get("sequence_number")
    curr_seq = curr.get("sequence_number")

    if (
        isinstance(prev_seq, int)
        and isinstance(curr_seq, int)
        and curr_seq < prev_seq
    ):
        resets.append((i+1, prev, curr))

print("Observed sequence decreases:", len(resets))

for index, prev, curr in resets[:30]:
    print(
        f"Record {index}: "
        f"{prev.get('sequence_number')} -> "
        f"{curr.get('sequence_number')}, "
        f"boot_id: {prev.get('boot_id', 'MISSING')} -> "
        f"{curr.get('boot_id', 'MISSING')}, "
        f"time: {curr.get('received_at')}"
    )

# 6. Quality distribution by calibration state
print("\n[6] QUALITY BY CALIBRATION")

matrix = Counter(
    (
        r.get("quality_flag", "MISSING"),
        r.get("load_calibrated", "MISSING")
    )
    for r in records
)

for (quality, calibration), count in sorted(
    matrix.items(), key=lambda x: str(x[0])
):
    print(
        f"quality={quality}, "
        f"load_calibrated={calibration}: {count}"
    )

print("\nInspection completed.")
