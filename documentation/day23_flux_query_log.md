
# Day 23: Flux Query Development and Testing Log

## Project
Karnaphuli Tunnel Structural Health Monitoring (SHM)

## Objective
Create and test Flux queries for retrieving telemetry,
temperature, and acceleration data from InfluxDB.

## Database
- Platform: InfluxDB OSS 2.9.1
- Bucket: tunnel_telemetry
- Query range: Last 1 hour

## Query Files
1. database/queries/all_data.flux
2. database/queries/temperature.flux
3. database/queries/vibration.flux

## Testing Results
- All-data query: PASS
- Temperature query: PASS
- Vibration query: PASS
- Dashboard sensor values: Visible
- Acceleration fields: Verified

## Conclusion
All three Flux query files were created and executed
successfully. Telemetry data, temperature readings,
and acceleration fields were verified in InfluxDB.

## Status
Day 23 completed.
