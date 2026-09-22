# Hardware attempt evidence — 2026-09-22 15:32 CST

## Later successful flash (supersedes earlier no-write status)

After a further owner-confirmed physical reset, USB re-enumerated as COM10,
303A:1001. ROM identified ESP32-S3-PICO-1 rev0.2, 8MB flash and 8MB PSRAM.
Full 8,388,608-byte backup is LOCAL ONLY at
`.delivery/sticks3-original-20260922.bin`, SHA256
`C37CF04CDF69814A1B7104CAF22B0FAA68BEE65E0B6FD5EC648E46B4207ACF89`.
esptool verify_flash compared all 8MB with device and reported digest matched.

Original table: nvs 0x9000/0x6000, phy_init 0xf000/0x1000, factory
0x10000/0x531000, sys 0x541000/0x100000, vfs 0x641000/0x1be000.
Only factory application at 0x10000 was replaced, 717456 bytes. App SHA256
`DCB0DCE7BF0C0AE5B41C88EE8947DF067F3AC27D63E4B5F5E614A075D2CDA079`.
Write completed in 4.9s, device hash verified. Erased sectors only 0x10000–0xbffff;
no full erase, no bootloader/partition/NVS/sys/vfs write.

RTS reset left ROM reachable; watchdog reset re-enumerated and application hello
then succeeded: protocol2, build pixel-0.1, ESP32-S3, width240 height135, board26
(confirmed M5GFX enum board_M5StickS3). Raw local evidence:
`.delivery/pixel-after-watchdog.ndjson`. Physical A counts changed, but owner
input correlation and screen appearance are still pending; not yet full QA.
Ongoing read-only 90s capture: `.delivery/pixel-physical-1.ndjson`.

Recovery: after verified ROM connection, original full backup can be restored at
0x0 using esptool write_flash (no erase_flash needed), only at owner's direction.
Do not upload the backup; it may contain previous private configuration.

## Earlier failed attempts

Observed after owner reported the light was on:

- Present USB composite device and COM9: VID 303A, PID 832B, Windows PnP status OK.
- esptool 4.9.0 `flash_id` default reset: Write timeout before chip identification.
- Explicit esp32s3/no_reset/two connection attempts: same Write timeout.
- No chip ID, no flash read, no backup created, no flash write or erase.
- Port processes exited; software retains coordination lease, not an open handle.
- Attempts stopped pending product task's single follow-up about flashing vs
  steady internal green light. No driver change, device restart or disassembly.

## Read-only diagnosis, not a confirmed cause

Installed esptool `loader.py:290` defines USB_JTAG_SERIAL_PID=0x1001 and line 676
uses it to choose USB reset. Espressif's official USB CDC flasher example also
opens 303A:1001 and says firmware using USB OTG may require manual download mode:
https://components.espressif.com/components/espressif/esp-serial-flasher/versions/1.6.0/examples/esp32_usb_cdc_acm_example?language=en

Initial search did not establish the 832B assignment. The later evidence below
supersedes that uncertainty. PID alone is still not a ROM-mode test.

StickS3's own instructions require USB connected and side reset held until the
internal green LED flashes: https://docs.m5stack.com/en/core/StickS3

Next acceptance: after the physical action, re-enumerate all present USB serial
devices (COM number/serial may change), identify the ROM with a successful
esptool response. Only that response enables backup and subsequent flashing.
If identity is unchanged and handshake still fails, report the exact result;
do not infer chip success from a light or force flash against an unidentified port.

## Follow-up: BPS / ready screen and application identity

Owner reported steady left light and BPS / ready on screen. A new bounded
no_reset/one-attempt flash_id still ended Write timeout; no flash operations.
Read-only Windows device properties then established:

- Composite and COM9 BusReportedDeviceDesc = `StickS3(UiFlow2)`.
- Composite parent is USB hub VID0BDA PID5411, not evidence of a separate UART
  downloader. Microsoft manufacturer field is the driver vendor, not device brand.
- Official M5Stack board source explicitly declares VID303A/PID832B and product
  `StickS3(UiFlow2)`, matching the live descriptor exactly:
  https://github.com/m5stack/uiflow-micropython/blob/master/m5stack/boards/M5STACK_StickS3/mpconfigboard.h
- Official startup `sticks3.py` UsbApp loads `/system/sticks3/usb.jpg`.
  Its relationship to the owner's exact visible BPS/ready has not yet been
  visually verified here. Do not call the app USB screen ROM download mode.
- Authorized REPL probe: 115200/DTR=true/RTS=false ctrl-C+CRLF returned write
  timeout; RTS=true with 2s settle and preliminary read returned empty then same
  timeout. No prompt received. No Python command or bootloader call sent.
- Upstream MicroPython v1.25 ESP32 modmachine.c has conditional ESP32-S3
  machine_bootloader_rtc implementation (force-download + restart), but actual
  firmware function availability was not verified because REPL is inaccessible.

Next smallest discriminator is the physical reset/download transition and fresh
USB enumeration/ROM response, coordinated once by product owner. Repeating ROM
commands against this unchanged application endpoint has not helped.
