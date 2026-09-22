# Reading bookmark prototype 0.2

135×240 portrait. Temporary monochrome fan-art assets from the art owner,
24 frames / Young and Grown; NOT a final character or completed care system.
No feeding, cleaning, paper completion or reading-position integration yet.

## Real controls

StickS3 BtnA=GPIO11, BtnB=GPIO12 per installed M5Unified0.2.22 and official pinmap.
The third side control is power/reset/download, never mapped as a business key.
A down edge gives immediate local feedback and exactly one interaction. Holding
does not repeat. B release under700ms saves a session marker; release at/over700ms
cycles reading/work/exercise/study context labels, without saving a marker first.
These labels do not claim domain features or score attention.

## Data

Preferences namespace pixelpet, versioned reading blob; newest16 markers retain
session sequence, elapsed-device-ms, interaction count, mode and marker ordinal.
`reading_query` returns newest8 to stay within bounded USB frame size. This is a
moment marker, NOT page number, ebook location or evidence of reading a paper.
Boot increments session; lifetime interactions and mode persist. Interaction
writes batch after2s idle or at30s, so sudden power loss can lose that unsaved
tail. Mark/mode writes immediately; every save is read back and compared. A
failure visibly reports unsaved state and latches further writes off until
restart, rather than repeatedly programming a damaged partition. Never one
flash write per A press.

100 lifetime physical interactions changes Young→Grown as an explicit demo
parameter, not final evolution design, reading progress or emotional inference.
There is no loss, punishment or absence decay.

## Compatibility and verification

Protocol2 kept. hello adds reading_session/interactions_lifetime/marks_total,
mode/growth_stage/storage_ok/state_selftest/display_ready/asset. Existing strict
Agent phrase whitelist and timeout remain; model cannot mutate bookmark state.
readingSelfTest executes pure state-machine cases on target: edge/hold, B699ms
mark vs700ms mode, uint32 rollover and marker attribution. It is not physical
button evidence. Hardware input/screen and nonzero-count restart still require
owner-observed checks. Asset script verification and firmware compilation are
separate evidence layers.

## 2026-09-22 persistence repair

The original UIFlow bootloader identified itself as IDF 5.4.2-dirty; this app
uses Arduino 2.0.17 / IDF 4.4.7. With that mixed boot chain, Preferences returned
the full write length but immediate readback returned NOT_FOUND. Raw NVS
inspection also found an invalid page-header CRC. Do not treat putBytes success
as persistence proof. Espressif does not guarantee newer bootloaders support
older apps: https://docs.espressif.com/projects/esp-idf/en/v5.2/esp32/api-guides/bootloader.html

Replacing only the bootloader with this build's matched ESP32-S3 image restored
immediate readback and cross-restart session persistence. This is observed
integration evidence; the precise low-level incompatibility is not proven.
No NVS erase command was issued, no partition table was changed. NVS runtime
recovery can modify its own damaged pages; preservation of all original NVS
keys is NOT claimed. Full original flash and diagnostic NVS snapshots remain
local and ignored, not in this repository.

- Bootloader: 15104 bytes at 0x0, erase footprint 0x0..0x3fff; SHA256
  `1776E4DD896A69D0A5C2E79957B0E2A88AA4129B1381D6478683515A1F6AF343`.
- App: 715376 bytes at 0x10000; SHA256
  `A6A46C122711407B13DF93C7C6BCEC70D3E21278D0097FF014FBEF2E4A7931C6`.
- Existing partition table at 0x8000 remains; nvs 0x9000/0x6000,
  factory app 0x10000/0x531000, sys/vfs unchanged by flash commands.
- Original boot-region backup: 32768 bytes; SHA256
  `0DD09AF935EF2D5CBFB179112F1D53EDB98D4632E2BA850EF494509368ED330B`,
  byte-identical to the same region of the original full-board backup.
- Local evidence: `.delivery/reading-storage-diagnostic1.ndjson` (failure),
  `.delivery/reading-matched-boot1.ndjson` (write/readback),
  `.delivery/reading-matched-boot2.ndjson` (loaded session1, current session2).
- `python bridge/check_storage.py --port COM10 --output NEW_LOG_PATH` sends only
  read-only requests. `storage_query` reports loaded length/schema/session and
  verified save status; it never injects user interactions or markers.
- Art owner revision f1a90cf is integrated unchanged; asset parity tests pass.

Hardware controls, nonzero *physical interaction/marker* persistence, physical
power-off recovery, actual portrait appearance and real-button Agent end-to-end
remain NOT_TESTED. Session1→2 proves a nonzero saved field survives a controlled
restart; it does not prove those other scenarios.

Includes proven StickS3 boot hotfix: correct only M5GFX/AUTODETECT cache to the
physically verified board26, 150ms PMIC settle, actual display-size check. The
pixel0.1 hotfix was flashed and3 distinct reset sessions returned240×135/board26/
display_ready=true. It does not prove portrait visual appearance.
