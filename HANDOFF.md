# Tenfold P0 handoff

## Frozen Android candidate

- Source: `6e2bf0e`
- APK: `android-app/out-release/tenfold-p0.apk` (local build artifact)
- APK SHA-256: `B9604D2572CAD083F2A72D1D95628985EFBDB565E93FA4B9A3BBFB19C76259A8`
- Signing certificate SHA-256: `EB55B62C374F6A58766625F52B83BA34B17E8A6B8C0D2CB95257781884CB153A`

The APK remains offline-capable and truthfully labels simulation, USB, offline rules and real-Agent states. The API key is Android-Keystore encrypted and no live credential was used.

## Firmware

`python -m platformio run -d firmware` completes successfully with the exact locks in `firmware/platformio.ini`. The release ZIP is produced locally from `firmware/release/p0/`; binaries are release assets and intentionally ignored by Git. Use `flash.ps1` in its default update mode to preserve NVS. Factory mode is only for an empty board and overwrites NVS.

- Final release ZIP: `D:\tenfold-worktrees\android\firmware\release\tenfold-firmware-p0-final.zip`
- ZIP SHA-256: `629A330BA42C19D713EAB3F454DF322A5099144627589B28FF294F12D2F9187A`
- App image SHA-256: `FB0EB0D71AF40097542D4DFC2E7E33245928E1E5FC80E89567F1DE132236EC09`
- Empty-board factory image SHA-256: `D89B76676EE6DB86D0BC433CC4F70C540C4651D5EE566A7507A4AE9938387789`

The hardware P0 is intentionally single-cycle. Phone archive does not close the board cycle. A different cycle ID is rejected until the owner has reconnected, confirmed every queued event is synchronized, and explicitly factory-reprovisioned the device. This prevents an automatic rollover from silently deleting offline facts.

The final ZIP also contains `THIRD_PARTY_NOTICES.md` and the actual license texts from the exact installed M5Unified, M5GFX, ArduinoJson and Arduino-ESP32 packages, plus the upstream ESP-IDF 4.4.7 license.

## Remaining physical acceptance

No M5StickS3 was available. A real-board owner must still verify first flash, Chinese screen layout, both physical key gestures, Android USB permission/CDC transport, persisted offer ACK, offline device event FIFO, disconnect/reconnect reconciliation and cold-boot time handshake. A live OpenAI-compatible Agent request also remains untested without a credential.
