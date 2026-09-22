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
tail. Mark/mode writes immediately; save failure visibly reported and retried
at a bounded rate. Never one flash write per A press.

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

Includes proven StickS3 boot hotfix: correct only M5GFX/AUTODETECT cache to the
physically verified board26, 150ms PMIC settle, actual display-size check. The
pixel0.1 hotfix was flashed and3 distinct reset sessions returned240×135/board26/
display_ready=true. It does not prove portrait visual appearance.
