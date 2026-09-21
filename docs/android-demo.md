# Tenfold Android + M5StickS3 P0

Package `io.tenfold.app`, version `0.1.0-p0` (`versionCode 1`), minSdk 26, targetSdk 35. The app is an offline-first ten-day commitment tool centered on “今天到这里，明天接得上”, not a general task manager.

## Truthful operating modes

- **模拟设备**: a complete local demo for first commitment, today card, complete/seal, stop note, recovery card, demo day advance and day-10 review. The UI always says it is simulated; it never claims a hardware ACK.
- **真实 USB**: Android USB Host opens a CDC-ACM data interface, performs line-coding/DTR initialization, then validates `protocol=1` and an `m5sticks3-*` device ID before sending business frames. “手机已保存” and “设备已确认” are separate facts.
- **离线规则**: fills a candidate card without a network request and labels itself `OFFLINE RULES`.
- **真实 Agent**: optional OpenAI-compatible HTTPS request with a strict JSON schema. Endpoint/model stay in app preferences; the API key is AES-GCM encrypted by Android Keystore. A response is a candidate and must still be confirmed. No credential was available during engineering, so a live cloud request remains unverified.

## Build and install

From the cloned repository root, with JDK tools on `PATH` and `ANDROID_HOME` pointing at an Android SDK containing platform/build-tools 35:

```powershell
& .\scripts\build-apk.ps1
& (Join-Path $env:ANDROID_HOME 'platform-tools\adb.exe') install -r .\android-app\out-release\tenfold-p0.apk
```

The script resolves its repository root from `PSScriptRoot`, only deletes the exact ignored `android-app/out-release` directory, asserts a root `classes.dex`, and signs with `.signing/tenfold-demo.jks`. The signing directory is ignored and the key is generated only once. Stable demo certificate SHA-256:

`EB55B62C374F6A58766625F52B83BA34B17E8A6B8C0D2CB95257781884CB153A`

The private key is local-only and must never be committed. A device holding an older APK signed by a different development key requires one explicit uninstall; subsequent builds from this signing directory support `adb install -r` and preserve app data.

## Connect the hardware

1. Flash the firmware below, then power the M5StickS3 normally.
2. Use a USB OTG-capable Android phone/tablet as host and a USB **data** cable. A charge-only cable cannot work.
3. In the app, create and confirm a card, open `设置与设备`, then choose `退出演示并连接 USB 设备`.
4. Allow Android's USB permission dialog. The app requests a fresh `hello`, queries persisted state, and either reconciles the matching command or sends the same pending offer.
5. Do not interpret “USB sent” as success. Only a matching `device_id/cycle_id/command_id/revision` response with `persisted:true` changes the UI to device-confirmed.
6. After delivery, the cable can be removed. The device keeps the card, state, event FIFO and two alternating checksummed snapshots in NVS.

Without a cable, the device can display the existing card, complete or seal after the explicit key sequence, and queue up to eight full event envelopes. On reconnect, envelopes replay in sequence and retain their original cycle/command/revision/day identity.

## Physical controls

- Hold **KEY1 + KEY2 together for 1 second**, then release both: open a 15-second operation window. The release is consumed and cannot become a business event.
- **KEY1 short click**: toggle between `完成` and `封存`.
- **KEY2 hold for 1.5 seconds**: persist the selected event, then show success/state. A normal short press and mechanical play do not write business events.
- After cold boot the clock is untrusted. View and seal remain available; complete is refused until a connected, validated phone sends a matching `set_time` frame.

The screen uses M5GFX `efontCN_12`, fits UTF-8 text by measured pixel width without splitting multibyte characters, and shows the actual confirmed action plus day/state. KEY1/KEY2 and USB must remain accessible in the mechanical enclosure.

## Build and flash firmware

```powershell
python -m pip install --user platformio
python -m platformio run -d firmware
python -m platformio run -d firmware -t upload --upload-port COMx
```

Enter StickS3 download mode using the official procedure (hold the reset/power control for about two seconds until its green LED indicates download mode), replace `COMx` with the enumerated port, and run the upload command. PlatformIO writes the board-defined bootloader/partition/app offsets; it does not issue a full-chip erase. Do not use `erase_flash` because that would remove NVS state.

The locked build completed successfully with PlatformIO Espressif32 6.12.0, M5Unified 0.2.22, M5GFX 0.2.29 and ArduinoJson 7.4.3. It used 22,684 bytes RAM (6.9%) and 716,517 bytes program space (21.4%). The release ZIP contains reusable, checksummed binaries; its manifest and flashing helper live under `firmware/release/p0/`.

The exact offsets emitted by the successful PlatformIO upload dry run are:

- `0x0000 bootloader.bin`
- `0x8000 partitions.bin`
- `0xe000 boot_app0.bin`
- `0x10000 firmware.bin`

For routine updates that preserve NVS state:

```powershell
powershell -File .\firmware\release\p0\flash.ps1 -Port COMx
```

Use `-Mode Provision` for the four exact PlatformIO segments on a new board. `-Mode Factory` writes `tenfold-p0-factory.bin` at address zero and fills the intervening address space; it is for an empty board only because it **overwrites the NVS gap and erases saved Tenfold state**. Never flash the standalone app binary at address zero.

The P0 board implementation is deliberately single-cycle. Phone-side archive does not close the board cycle; a different `cycle_id` is rejected as `cycle_conflict`. To bind another cycle, first reconnect and verify that no device events remain pending/unconfirmed, then explicitly use `-Mode Factory` and reprovision. This limitation avoids silently discarding an offline hardware event queue; automatic multi-cycle board rollover has not been real-hardware tested.

## Protocol v1

UTF-8 newline JSON, maximum 4096 bytes. Oversize frames are discarded through the next newline on both sides.

- Host: `hello_request`, `query`, `offer`, `set_time`, `event`, `event_ack`.
- Device: `hello`, `status`, `ack`, `time_ack`, `event`, `event_ack`, `error`.
- `offer` includes protocol, command/cycle/revision/day, cycle dates/time zone, confirmed short action, completion condition, stop time and recovery step.
- Duplicate offers replay ACK only for an already committed snapshot. Host events are strictly sequential and idempotent. Device events use a persistent FIFO of complete envelopes.
- Firmware mutates candidate RAM, verifies the inactive NVS slot and checksum, commits the active marker, and only then advances the in-memory version or returns `persisted:true`.

## Sources and licenses

- [Android USB Host API](https://developer.android.com/develop/connectivity/usb/host) — official Android documentation used for permission, interface claiming and worker-thread transfers.
- [M5StickS3 official documentation](https://docs.m5stack.com/en/core/StickS3) and [button API](https://docs.m5stack.com/en/arduino/m5sticks3/button) — board/build/button behavior.
- [M5Unified](https://github.com/m5stack/M5Unified) 0.2.22 and [M5GFX](https://github.com/m5stack/M5GFX) 0.2.29 — MIT License; firmware board, display, font and button support.
- [ArduinoJson](https://github.com/bblanchon/ArduinoJson) 7.4.3 — MIT License; exact PlatformIO lock for strict parsing.
- [usb-serial-for-android](https://github.com/mik3y/usb-serial-for-android) — MIT License; reviewed as the fallback if the current single-board CDC implementation fails real OTG testing. It is not bundled in this dependency-free APK.

The firmware release ZIP includes `THIRD_PARTY_NOTICES.md` and the actual license texts copied from the exact installed M5Unified, M5GFX, ArduinoJson and Arduino-ESP32 packages, together with the upstream ESP-IDF 4.4.7 license.

No M5StickS3 was connected during implementation. The firmware was compiled and linked, and a no-device upload dry run verified the offsets, but that evidence does not replace the required real-phone OTG + real-board offer/ACK/offline-key/reconnect test.
