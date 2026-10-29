# Day 20: ESP32 HTTP Telemetry Publisher

## 1. Objective

To transmit sensor telemetry from the ESP32 to the Flask-based HTTP ingestion API as part of the Karnaphuli Tunnel Structural Health Monitoring (SHM) prototype.

This implementation uses HTTP POST to send JSON-formatted sensor readings to `http_ingest_api.py`.

**Communication method implemented:** HTTP  
**MQTT implementation status:** Not implemented in this firmware

## 2. Firmware Location

Firmware file:

`firmware/09_mqtt_publisher/09_mqtt_publisher.ino`

**Important:** Although the firmware is stored in the `09_mqtt_publisher` directory, the supplied code implements HTTP communication, not MQTT. The folder name does not determine the communication protocol.

## 3. Hardware Components

- ESP32 DOIT DEVKIT V1
- DHT22 temperature and humidity sensor
- MPU6050 accelerometer and gyroscope
- HW-038 analog water sensor
- 5 kg load cell
- HX711 load-cell amplifier
- USB cable and jumper wires

## 4. Sensor Pin Configuration

| Component | ESP32 connection |
|---|---|
| DHT22 data | GPIO 4 |
| MPU6050 SDA | GPIO 21 |
| MPU6050 SCL | GPIO 22 |
| HW-038 analog output | GPIO 34 |
| HX711 DOUT | GPIO 18 |
| HX711 SCK | GPIO 19 |

## 5. Software and Libraries

- Arduino IDE
- ESP32 Arduino core
- WiFi library
- HTTPClient library
- Wire library
- DHT sensor library
- Adafruit MPU6050 library
- Adafruit Unified Sensor library
- HX711 library

## 6. Wi-Fi and API Configuration

The ESP32 connects to the configured Wi-Fi network and sends telemetry to the laptop's Flask API.

- Wi-Fi SSID: `Bachelor`
- API endpoint: `http://192.168.0.107:5000/telemetry`
- HTTP method: `POST`
- Content type: `application/json`
- Publish interval: 1 second
- HTTP timeout: 3000 milliseconds
- Wi-Fi reconnection interval: 5000 milliseconds

The API address must match the laptop's current local IPv4 address. Wi-Fi credentials should not be published in shared documentation.

## 7. Sensor Reading and Telemetry

### DHT22
- Measures temperature in degrees Celsius.
- Measures relative humidity in percent.
- Reading interval: 2 seconds.
- The previous valid reading is retained when a new reading fails.

### MPU6050
- Reads acceleration along the X, Y and Z axes.
- Uses I2C communication on GPIO 21 and GPIO 22.

### Water Sensor
- Reads the analog sensor output through GPIO 34.
- Sends the raw ADC value as `water_raw`.

### HX711 and Load Cell
- Reads the raw HX711 value when the module is ready.
- Sends the raw reading as `load_raw`.
- `load_kg` is currently set to `0.0` as a placeholder because calibration has not been confirmed.

The placeholder value must not be interpreted as a measured weight.

## 8. JSON Telemetry Payload

The firmware constructs a JSON payload containing:

- `device_id`
- `gateway_id`
- `zone_id`
- `temperature`
- `humidity`
- `accel_x`
- `accel_y`
- `accel_z`
- `water_raw`
- `load_raw`
- `load_kg`
- `dht_valid`
- `mpu_valid`
- `hx711_valid`
- `quality_flag`

The payload is transmitted to the Flask API using HTTP POST.

## 9. HTTP Transmission Workflow

1. Initialize the sensors.
2. Connect the ESP32 to Wi-Fi.
3. Read sensor values at the configured intervals.
4. Construct the JSON telemetry payload.
5. Send the payload to the Flask API.
6. Print sensor readings, HTTP status, API response and payload in the Arduino Serial Monitor.
7. The Flask API processes the request and forwards the data to InfluxDB if its ingestion configuration is correct.

## 10. Testing and Verification

| Test | Status |
|---|---|
| Firmware compilation | Pending verification |
| ESP32 Wi-Fi connection | Pending verification |
| Sensor initialization | Pending verification |
| HTTP POST request | Pending verification |
| Flask API response | Pending verification |
| InfluxDB data storage | Pending verification |
| InfluxDB table visualization | Pending verification |
| InfluxDB graph visualization | Pending verification |

### HTTP Status Interpretation

- `200` or `201`: The API reports successful processing; verify the InfluxDB write as well.
- `400`: The request or payload may be invalid.
- `500`: The server encountered an error.
- Negative HTTP status: Check connectivity, the API address and the HTTP client error message.

Record the actual status and response from the Serial Monitor after testing.

## 11. InfluxDB Verification

The target measurement is expected to be:

`tunnel_telemetry`

The expected sensor fields include:

- `temperature`
- `humidity`
- `accel_x`
- `accel_y`
- `accel_z`
- `water_raw`
- `load_kg`

The actual measurement, bucket, tags and field mappings must match the Flask API implementation.

Verify that new records appear in the InfluxDB Data Explorer with recent timestamps. Capture both the table and graph views if available.

## 12. Evidence and Screenshots

Save actual screenshots under:

`hardware/photos/`

Recommended filenames:

1. `day20_esp32_upload.png` — firmware upload result.
2. `day20_flask_api.png` — Flask terminal showing incoming POST requests.
3. `day20_influxdb_table.png` — sensor telemetry in table form.
4. `day20_influxdb_graph.png` — sensor telemetry graph.

Only include screenshots captured from the actual project environment.

## 13. Limitations

- This firmware uses HTTP POST rather than MQTT.
- The MQTT broker and Python MQTT consumer are not used by this code.
- The load-cell calibration is not confirmed; `load_kg` is a placeholder.
- Invalid sensor readings may be represented by zero values. The validity flags should be checked before interpreting these values as actual measurements.
- The firmware currently sets `quality_flag` to `partial` when all checked sensors are available, and `degraded` otherwise. This logic should be reviewed before interpreting the flag as a data-quality assessment.

## 14. Output Files

- `firmware/09_mqtt_publisher/09_mqtt_publisher.ino`
- `documentation/mqtt_esp32_log.md` (rename recommended if documenting HTTP only)
- `hardware/photos/day20_esp32_upload.png`
- `hardware/photos/day20_serial_monitor_http.png`
- `hardware/photos/day20_flask_api.png`
- `hardware/photos/day20_influxdb_table.png`
- `hardware/photos/day20_influxdb_graph.png`

## 15. Completion Criteria

The HTTP telemetry implementation can be considered verified when the ESP32 sends valid JSON requests, the Flask API accepts them, and the expected new sensor records are confirmed in InfluxDB.

This does not establish completion of the MQTT publisher task. MQTT requires a separate firmware implementation and verification through the MQTT broker and Python consumer.
