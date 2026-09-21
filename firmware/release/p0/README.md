# Tenfold P0 firmware package

These binaries were produced by `python -m platformio run -d firmware` with the locked dependencies in `firmware/platformio.ini`.

- Normal update, preserving NVS state: `powershell -File firmware/release/p0/flash.ps1 -Port COM5`
- First provisioning with exact PlatformIO offsets: add `-Mode Provision`.
- Empty-board factory image: add `-Mode Factory`. This merged image fills address gaps and **overwrites NVS state**; do not use it for routine updates.

Verify the package against `SHA256SUMS.txt` before flashing. Replace `COM5` with the enumerated serial port. No physical M5StickS3 was available during this build, so flashing and hardware I/O remain explicitly unverified.

Dependency versions, source locations, notices and the actual license texts shipped with this binary are in `THIRD_PARTY_NOTICES.md` and `licenses/`.

This P0 board protocol intentionally binds one cycle ID. Archiving on the phone does not close or erase the board cycle, and an offer with a different cycle ID returns `cycle_conflict`. Before binding a later cycle, reconnect and confirm that all queued device events have reached the phone. Then explicitly run `-Mode Factory` to erase the old NVS state and reprovision; never reset while the phone still reports pending or unconfirmed device data.
