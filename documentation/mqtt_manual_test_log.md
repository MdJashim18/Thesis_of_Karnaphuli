# Day 17: MQTT Authentication and Manual Test Log

## Objective
To verify MQTT username/password authentication and test message delivery between a publisher and subscriber.

## Environment
- Operating System: Windows
- MQTT Broker: Mosquitto 2.1.2
- Host: `127.0.0.1`
- Port: `1883`
- Username: `sensor_user`

## MQTT Topic
`karnaphuli/tunnel/LAB_PROTOTYPE/GW-LAB-001/telemetry`

## Test Payload
```json
{
  "temperature": 28.4,
  "humidity": 72.1
}
```

## Test Procedure
1. Started the Mosquitto broker using the project configuration.
2. Started the subscriber with MQTT username/password authentication.
3. Published the JSON telemetry message using `mosquitto_pub`.
4. Verified the received message in the subscriber terminal.
5. Captured a screenshot of the subscriber output.

## Actual Result
The subscriber received the following message successfully:

`karnaphuli/tunnel/LAB_PROTOTYPE/GW-LAB-001/telemetry {"temperature":28.4,"humidity":72.1}`

## Authentication Status
PASS — Valid credentials were used for the subscriber and publisher, and the message was received.

## Message Delivery Status
PASS — The expected JSON message appeared in the subscriber terminal.

## Evidence
- Screenshot: `documentation/screenshots/day17_mqtt_subscriber.png`

## Conclusion
The MQTT manual publishing and subscription test completed successfully using username/password authentication.

## Security Note
The actual MQTT password is not stored in this log.
