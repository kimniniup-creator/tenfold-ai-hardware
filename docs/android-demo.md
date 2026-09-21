# Android P0 demo

Package: `io.tenfold.app`. The APK is intentionally dependency-free (Android framework Java) so it can be built with the installed SDK build tools.

## Truthful modes

- **USB DEVICE**: Android USB Host opens a discovered bulk OUT endpoint, requests Android's system USB permission, and sends newline JSON. A transmission is not an ACK; M5 firmware responds only after its local `Preferences` write.
- **SIMULATED DEVICE**: no device is discovered. It is a local UI demonstration only and is labelled on every main state; it cannot claim hardware delivery.
- **OFFLINE RULES**: the proposal screen says no LLM call was made. It compresses the user's lines into 1 goal / up to 3 outcomes / 1 action and preserves remaining lines in Parking Lot. No task text is sent to a cloud service.

## Wire protocol v1

One UTF-8 JSON object per line; maximum 4096 bytes. App `offer` includes `command_id`, `cycle_id`, `revision`, `day_index`, `action_short`, `done_when_short`, and `stop_at`. Firmware replies `ack` only after persistence. `event` has `seq`, `cycle_id`, and `event_type`; firmware persists it before replying. Reject unknown types and oversize messages. This P0 USB dev route is not production authentication or BLE.

## Sources and licenses

- [Android USB host API](https://developer.android.com/develop/connectivity/usb/host) — Android SDK documentation; Android USB access design.
- [M5StickS3 official docs](https://docs.m5stack.com/en/core/StickS3) — M5Stack docs; PlatformIO flags and board capability reference.
- [M5Unified](https://github.com/m5stack/M5Unified) — MIT License, used by the firmware build definition.
- [ArduinoJson](https://arduinojson.org/) is deliberately **not** included: P0 parser has only fixed demo messages; production must add a strict JSON parser with its license tracked.

No M5 board was connected during this implementation. Firmware source is provided but not flashed or hardware-tested.
