# Hardware attempt evidence — 2026-09-22 15:32 CST

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
