# Demo 3 - Sensors to silicon, locally (~3 min on stage)

Phone IMU -> hub -> MQTT `phone/sensors` -> this subscriber -> local
"hardware execution loop".

Talk beat (Sistem Komputer): low-latency network protocols and edge
interfacing - the same MQTT pattern real embedded and IoT fleets run on.
Courses on the slide: Interfacing, Sistem Tertanam, Komunikasi Data.

## Run

1. Hub running, phone Motion toggle on.
2. `python demo3_sensor_mqtt/main.py`
3. Shake or tilt the phone - shake events fire the hardware loop.

## Notes

- `on_shake()` is deliberately a stub: drop in gpiozero (Raspberry Pi LED),
  pyserial (Arduino), or a beep. On stage, the scrolling event log IS the
  demo - the audience sees bytes arriving as the phone moves.
- `--broker test.mosquitto.org` exists only for rehearsal without a local
  broker. On show day: local broker, no internet. The protocol is the point.
- Latency budget to name-drop: phone -> broker -> loop in tens of ms on Wi-Fi.
