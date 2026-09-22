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

This proves 832B is not that built-in Serial/JTAG PID. It does NOT establish that
832B is application CDC, nor which firmware currently runs. No authoritative
832B assignment was found. PID alone is not a ROM-mode test.

StickS3's own instructions require USB connected and side reset held until the
internal green LED flashes: https://docs.m5stack.com/en/core/StickS3

Next acceptance: after the physical action, re-enumerate all present USB serial
devices (COM number/serial may change), identify the ROM with a successful
esptool response. Only that response enables backup and subsequent flashing.
If identity is unchanged and handshake still fails, report the exact result;
do not infer chip success from a light or force flash against an unidentified port.
