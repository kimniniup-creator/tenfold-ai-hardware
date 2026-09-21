# Tenfold P0 firmware package

These binaries were produced by `python -m platformio run -d firmware` with the locked dependencies in `firmware/platformio.ini`.

- Normal update, preserving NVS state: `powershell -File firmware/release/p0/flash.ps1 -Port COM5`
- First provisioning with exact PlatformIO offsets: add `-Mode Provision`.
- Empty-board factory image: add `-Mode Factory`. This merged image fills address gaps and **overwrites NVS state**; do not use it for routine updates.

Verify the package against `SHA256SUMS.txt` before flashing. Replace `COM5` with the enumerated serial port. No physical M5StickS3 was available during this build, so flashing and hardware I/O remain explicitly unverified.
