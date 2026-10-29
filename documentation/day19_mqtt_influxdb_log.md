# Day 19: MQTT Consumer and InfluxDB Integration Log

## Objective
To connect the MQTT broker with InfluxDB using a Python MQTT consumer and store tunnel structural health monitoring (SHM) sensor telemetry data for visualization and analysis.

## Software and Tools
- Operating System: Windows
- Python
- MQTT Broker: Mosquitto
- InfluxDB OSS 2.9.1
- InfluxDB Data Explorer
- Python MQTT client and InfluxDB client libraries

## Project Configuration
- Project directory: `D:\karnaphuli-shm-month2`
- Environment configuration: `.env`
- Python consumer script: `python/mqtt_consumer.py`
- InfluxDB URL: `http://localhost:8086`
- MQTT broker: `127.0.0.1:1883`
- MQTT topic: `karnaphuli/tunnel/+/+/telemetry`
- InfluxDB bucket: `tunnel_telemetry`
- Measurement: `tunnel_telemetry`

## Implementation Summary
1. Configured InfluxDB connection settings and authentication token in the `.env` file.
2. Created and executed the Python MQTT consumer.
3. Connected the consumer to the local Mosquitto MQTT broker.
4. Subscribed to the tunnel telemetry topic.
5. Received sensor telemetry messages from the MQTT broker.
6. Wrote the received sensor data to InfluxDB.
7. Opened InfluxDB Data Explorer and verified that the test sensor data was visible.

## Successful Test Output

```text
Connecting to MQTT broker 127.0.0.1:1883...
MQTT connected successfully
Subscribing to: karnaphuli/tunnel/+/+/telemetry
Written to InfluxDB: {
  'device_id': 'ESP32-GW-LAB-001',
  'gateway_id': 'gateway01',
  'zone_id': 'LAB_PROTOTYPE',
  'temperature': 32.5,
  'humidity': 91.3,
  'accel_x': 0.8,
  'accel_y': 0.0,
  'accel_z': 10.9,
  'water_raw': 665,
  'load_kg': 0.0,
  'quality_flag': 'GOOD'
}
```

## Sensor Fields
The test telemetry included the following fields:

- `temperature`: Temperature reading in °C
- `humidity`: Relative humidity in %
- `accel_x`, `accel_y`, `accel_z`: Accelerometer readings
- `water_raw`: Raw water sensor reading
- `load_kg`: Load-cell weight value in kg
- `device_id`: Sensor device identifier
- `gateway_id`: Gateway identifier
- `zone_id`: Prototype monitoring zone
- `quality_flag`: Data quality status

## Issues and Observations
- An initial InfluxDB `401 Unauthorized` error occurred because of authentication configuration. A new API token with the required write permission was configured, and data writing subsequently succeeded.
- A Python MQTT client deprecation warning appeared. It did not prevent the consumer from connecting or writing data.
- Data was visible in InfluxDB Data Explorer after adjusting the Flux query.
- The successful test confirms the MQTT-to-Python-to-InfluxDB data path for the test message.
- The previous 900-record dataset has not yet been confirmed as imported into InfluxDB. Its presence in the local JSONL file alone does not confirm database ingestion.

## Result
**Day 19 main integration test: SUCCESSFUL.**

The Python consumer connected to Mosquitto, subscribed to the telemetry topic, received a test message, and successfully wrote the sensor data to InfluxDB. Data Explorer also displayed the test data.

## Files and Directories

```text
karnaphuli-shm-month2/
├── .env
├── python/
│   └── mqtt_consumer.py
└── documentation/
    └── day19_mqtt_influxdb_log.md
```

## Next Steps
- Verify whether the 900-record dataset has been ingested into InfluxDB.
- If necessary, import or publish the historical records.
- Continue developing sensor data visualization and monitoring features.

## Conclusion
The main objective of Day 19 was achieved. The MQTT consumer and InfluxDB integration is working for the verified test message, providing a foundation for storing and visualizing sensor telemetry in the Karnaphuli Tunnel SHM prototype.