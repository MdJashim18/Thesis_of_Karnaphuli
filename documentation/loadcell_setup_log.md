# Day 10: Load Cell and HX711 Setup Log

## Objective

Connect a 5 kg bar-type load cell to an HX711 amplifier and interface it with an ESP32 to obtain initial raw readings for load measurement.

## Hardware Components

- ESP32 DOIT DEVKIT V1
- 5 kg bar-type load cell
- HX711 amplifier module
- Jumper wires
- Mounting base and screws
- Known test load (approximately 100–200 g)

## Wiring

- HX711 DT/DOUT → ESP32 GPIO 18
- HX711 SCK/CLK → ESP32 GPIO 19
- HX711 GND → ESP32 GND
- HX711 VCC → Compatible supply voltage
- Load cell E+, E−, A+, and A− → Corresponding HX711 terminals according to the load cell's wire mapping

**Note:** The supply voltage and load cell wire mapping should be confirmed against the specific module and load cell documentation.

## Test Procedure

1. Connected the load cell to the HX711 amplifier.
2. Connected the HX711 to the ESP32 using GPIO 18 (DT) and GPIO 19 (SCK).
3. Uploaded the HX711 response test program.
4. Collected 10 averaged readings without an external load.
5. Applied a known test load of approximately 100–200 g at the designated loading point.
6. Collected another 10 averaged readings using the same program.
7. Compared the mean readings under the two test conditions.

## Observed Results

### Test 1: No External Load

- Number of readings: 10
- Readings: 2463, 2476, 2467, 2464, 2466, 2462, 2471, 2460, 2470, 2466
- Mean reading: 2466.5
- Minimum reading: 2460
- Maximum reading: 2476

### Test 2: With a Known Test Load

- Number of readings: 10
- Readings: 2465, 2468, 2469, 2458, 2464, 2472, 2466, 2467, 2474, 2468
- Mean reading: 2467.1
- Minimum reading: 2458
- Maximum reading: 2474

### Comparison

- No-load mean: 2466.5
- Loaded mean: 2467.1
- Difference between means: 0.6 counts

The two sets of readings have substantially overlapping ranges. No clear load-dependent change was observed in this test.

**Note:** An earlier test recorded a no-load mean of 2467.0 and a loaded mean of 2469.5, a difference of 2.5 counts. These earlier results are retained as preliminary observations and are separate from the latest 10-reading test.

## Status

- Physical wiring and mounting checks completed.
- Initial serial output obtained from the HX711 interface.
- Ten averaged readings collected under each of two test conditions.
- Load-dependent response not yet clearly distinguishable.
- Calibration and reliable weight measurement remain pending.

## Evidence

- `hardware/wiring_diagram/06_loadcell_hx711_esp32.png`
- `hardware/photos/loadcell_wiring.jpg`

## Limitations

The mean raw reading changed by only 0.6 counts between the latest no-load and loaded tests. This difference is too small to establish reliable load measurement from the available observations.

The cause has not yet been identified. Further investigation should include verification of the HX711 output format and library behavior, load cell terminal mapping, electrical connections, mechanical mounting, and response to repeated known loads.

The readings reported here are the values printed by the current test program. Their interpretation as actual HX711 ADC raw counts should be confirmed before calibration.

## Next Steps

1. Verify the HX711 module's supply voltage and electrical connections.
2. Recheck the load cell wire mapping against its documentation.
3. Inspect the fixed end and loading point of the bar-type load cell.
4. Confirm that the program and library return the expected raw measurement values.
5. Repeat no-load and known-load tests several times under consistent conditions.
6. Proceed to calibration only after a repeatable load-dependent response is observed.

## Date

2026-10-23