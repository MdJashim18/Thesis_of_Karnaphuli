# Day 16: Mosquitto MQTT Broker Setup and Communication Test

## Objective
Install and configure the Mosquitto MQTT broker on Windows, enable username/password authentication, and verify communication between an MQTT publisher and subscriber.

## Environment
- Operating System: Windows 11
- Mosquitto Version: 2.1.2
- Broker Address: `127.0.0.1`
- MQTT Port: `1883`
- MQTT Username: `sensor_user`
- Authentication: Enabled
- Configuration File: `mqtt/mosquitto.conf`
- Password File: `mqtt/passwordfile`

## Broker Configuration
The broker was configured with the following settings:

- Listener: `127.0.0.1:1883`
- Anonymous access: Disabled
- Password file: `mqtt/passwordfile`

The configuration test returned:

`Configuration file is OK.`

The broker started successfully and reported:

`mosquitto version 2.1.2 running`

## Communication Test

### Subscriber
The subscriber connected using the configured username and password and subscribed to:

`karnaphuli/tunnel/#`

The broker log confirmed that the client connected and the subscription was acknowledged.

### Publisher
A test message was published to:

`karnaphuli/tunnel/test`

Message:

`Day 16 MQTT test successful`

### Received Output
The subscriber successfully received:

`karnaphuli/tunnel/test Day 16 MQTT test successful`

## Results
- [x] Mosquitto broker installed and launched.
- [x] Configuration file validated.
- [x] Username/password authentication verified.
- [x] Subscriber connected and subscribed successfully.
- [x] Publisher sent a test message.
- [x] Subscriber received the published message.

## Limitations and Security Notes
The broker currently listens only on `127.0.0.1`, so it accepts connections from the same computer. The ESP32 cannot connect using this loopback address. A properly secured LAN listener and appropriate firewall settings will be required for future ESP32-to-broker communication.

The password is intentionally excluded from this documentation.

## Conclusion
The local MQTT communication pipeline was successfully tested. This provides a foundation for integrating sensor telemetry from the Karnaphuli tunnel monitoring prototype in a later stage.
