# Day 5 CSV Final Verification — ESP32 + DHT22

## Verification result

**Status: NOT FULLY VERIFIED — the available CSV contains 99 readings, not 100.**

This audit was run against `dht22_day5_verified.csv` available in the working files. It checks the file's structure and values; it cannot establish that this file is byte-for-byte identical to the CSV saved directly from the user's Arduino/Serial Monitor workflow unless that original file is supplied.

## Checks

| Check | Result |
|---|---|
| Expected columns (`timestamp,temperature,humidity`) | PASS |
| Number of data rows | 99 |
| Target of 100 readings | FAIL — 1 reading short |
| First timestamp | 2 s |
| Last timestamp | 198 s |
| Every interval is 2 seconds | PASS |
| Missing/blank values | 0 |
| Temperature range | 32.0–32.2 °C |
| Mean temperature | 32.09 °C |
| Humidity range | 90.1–91.5 %RH |
| Mean humidity | 91.02 %RH |

## What remains

The timestamps run from 2 s to 198 s, in 2-second increments. That is 99 readings. The 0-second reading is absent. **Do not invent a row or copy another reading to make the file contain 100.**

To complete Day 5 accurately:
1. Run the ESP32 sketch again with `delay(2000)` and a counter that records exactly 100 successful readings.
2. Save/export the new output as `data/raw/dht22_day5.csv`, with the header `timestamp,temperature,humidity` and timestamps from 0 through 198 seconds.
3. Upload that actual CSV here. I can then run the final verification against the real file and update the report/workbook.

## Data-quality interpretation

The available file has no blank values and the timestamp spacing is consistently 2 seconds. These checks show the supplied rows are structurally consistent, but they do not prove sensor accuracy. The phone weather app in the photo is not a calibrated reference thermometer, so it should not be reported as a reference-device validation.
