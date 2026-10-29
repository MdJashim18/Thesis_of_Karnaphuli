
import json
import paho.mqtt.client as mqtt

from influxdb_client import InfluxDBClient, Point, WritePrecision
from influxdb_client.client.write_api import SYNCHRONOUS

from config import (
    MQTT_BROKER,
    MQTT_PORT,
    MQTT_USER,
    MQTT_PASS,
    MQTT_TOPIC,
    INFLUXDB_URL,
    INFLUXDB_TOKEN,
    INFLUXDB_ORG,
    INFLUXDB_BUCKET,
)

# Check required configuration
required_values = {
    "MQTT_PASS": MQTT_PASS,
    "INFLUXDB_TOKEN": INFLUXDB_TOKEN,
    "INFLUXDB_ORG": INFLUXDB_ORG,
    "INFLUXDB_BUCKET": INFLUXDB_BUCKET,
}

missing = [name for name, value in required_values.items() if not value]

if missing:
    raise ValueError(
        "Missing configuration in .env: " + ", ".join(missing)
    )

# Connect to InfluxDB
influx_client = InfluxDBClient(
    url=INFLUXDB_URL,
    token=INFLUXDB_TOKEN,
    org=INFLUXDB_ORG,
)

write_api = influx_client.write_api(
    write_options=SYNCHRONOUS
)


def on_connect(client, userdata, flags, rc):
    if rc == 0:
        print("MQTT connected successfully")
        print(f"Subscribing to: {MQTT_TOPIC}")
        client.subscribe(MQTT_TOPIC)
    else:
        print(f"MQTT connection failed. Result code: {rc}")


def on_message(client, userdata, msg):
    try:
        payload = json.loads(msg.payload.decode("utf-8"))

        point = (
            Point("tunnel_telemetry")
            .tag("device_id", str(payload.get("device_id", "unknown")))
            .tag("gateway_id", str(payload.get("gateway_id", "unknown")))
            .tag("zone_id", str(payload.get("zone_id", "unknown")))
            .tag("quality_flag", str(payload.get("quality_flag", "unknown")))
            .field("temperature", float(payload.get("temperature", 0)))
            .field("humidity", float(payload.get("humidity", 0)))
            .field("accel_x", float(payload.get("accel_x", 0)))
            .field("accel_y", float(payload.get("accel_y", 0)))
            .field("accel_z", float(payload.get("accel_z", 0)))
            .field("water_raw", int(payload.get("water_raw", 0)))
            .field("load_kg", float(payload.get("load_kg", 0)))
        )

        # InfluxDB assigns the write time when no timestamp is supplied.
        # This avoids interpreting an ESP32 uptime counter as a real date.
        write_api.write(
            bucket=INFLUXDB_BUCKET,
            org=INFLUXDB_ORG,
            record=point,
        )

        print(f"Written to InfluxDB: {payload}")

    except (ValueError, TypeError, KeyError, UnicodeDecodeError) as e:
        print(f"Invalid MQTT message: {e}")

    except Exception as e:
        print(f"Processing/InfluxDB error: {e}")


# Use Callback API v1 for the callback signatures above.
client = mqtt.Client(mqtt.CallbackAPIVersion.VERSION1)

client.username_pw_set(MQTT_USER, MQTT_PASS)
client.on_connect = on_connect
client.on_message = on_message

try:
    print(f"Connecting to MQTT broker {MQTT_BROKER}:{MQTT_PORT}...")
    client.connect(MQTT_BROKER, MQTT_PORT, 60)
    client.loop_forever()

except KeyboardInterrupt:
    print("\nMQTT consumer stopped by user.")

except Exception as e:
    print(f"MQTT connection error: {e}")

finally:
    client.disconnect()
    write_api.close()
    influx_client.close()
