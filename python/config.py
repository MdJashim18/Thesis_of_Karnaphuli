
import os
from dotenv import load_dotenv

load_dotenv()

# MQTT configuration
MQTT_BROKER = "127.0.0.1"
MQTT_PORT = 1883
MQTT_USER = "sensor_user"
MQTT_PASS = os.getenv("MQTT_PASS")
MQTT_TOPIC = "karnaphuli/tunnel/+/+/telemetry"

# InfluxDB configuration
INFLUXDB_URL = "http://localhost:8086"
INFLUXDB_TOKEN = os.getenv("INFLUXDB_TOKEN")
INFLUXDB_ORG = os.getenv("INFLUXDB_ORG")
INFLUXDB_BUCKET = os.getenv("INFLUXDB_BUCKET")
