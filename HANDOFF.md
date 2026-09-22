# Tenfold P0 handoff

## Historical integration: pixel companion

Host implementation integrated and verified: 6 direct regression tests, independent scoped host checks, full PlatformIO build, deterministic art assets. Final entry is README.md and docs/pixel-companion/SOFTWARE.md. No board flash or physical button/screen pass yet. Resume software task after Kim reports green LED/download mode; capture original flash locally before writing. Do not launch bridge and capture_device simultaneously.

Kim replaced the active product scope on 2026-09-22: native M5 buttons for playful interaction, rhythm summaries as Agent context, original retro pixel companion on the M5 screen, no new enclosure. See docs/hackathon/product/PIXEL_COMPANION_PRD.md. Product task 01a0c5b4-a19c-7810-8c6e-d8a87bb68f70 coordinates integration in D:/tenfold-worktrees/pixel-integration. Software owns the sole COM9 lease for identification, backup and new firmware flashing; testing must wait for explicit release. The historical delivery below remains recoverable but is not the current requirements baseline.
## Latest: USB reconnect repair before task-growth migration

Reproduced backpressure/reopen stall fixed and tested twice without reset.
See docs/pixel-companion/TRANSPORT.md for root-cause boundary, tests and evidence.
App09E04A4FC38973040FF2F95B46A32685D8BD785192460565992AEE122CE10B11,
716256bytes; bootloader unchanged. Device session7,lifetime188,marks4,135x240.
Eleven host tests pass. COM10 exclusive ownership remains this task.
Next authorized implementation: read main commit7f260d2 contract
docs/hackathon/product/TASK_GROWTH_CONTRACT.md; integrate art6d5981e unchanged.
Growth is task-node completion ONLY; old100-click growth below is superseded,
not a current accepted product rule.

## Current: portrait reading prototype, matched boot chain (2026-09-22)

Latest app-only update source eaef7c0: SHA256
81182568C419208C2E93F5537583915A7492E7E0EE984C691BA791CA8BE5ED5F,
715248bytes. Matched bootloader unchanged. Fault text asks restart. Reading Agent
entry/rendering NOT integrated, candidate alwaysfalse (real6-press rhythm
verified), no automatic requests. After app update session5 retained lifetime25
and mark1;135x240/board26/storage_ok/selftest true. Live inputs reached48, not
restart-tested at48. COM10 released after capture; no further reset during user
input. Intermittent no-reply after reopening still unresolved. See READing docs
for exact evidence. A6A46C hash below is historical repair app.

Current branch codex/pixel-firmware in D:/tenfold-worktrees/pixel-firmware.
Exclusive device port COM10. Board is running, not left in ROM. 135x240,
board26/display_ready, art f1a90cf. Do not use historical COM9 instructions below.
Reading persistence required matching the old Arduino/IDF4 app with its own
bootloader instead of the original UIFlow IDF5.4.2 bootloader. Before repair,
putBytes reported success while immediate readback failed. After scoped boot+app
write, session1→2→3 persisted with exact340-byte schema readback. No NVS erase
command or partition-table change. Recovery backups and logs remain .delivery,
not Git; exact hashes/bounds and remaining untested cases are in
docs/pixel-companion/READING.md. Current app SHA A6A46C122711407B13DF93C7C6BCEC70D3E21278D0097FF014FBEF2E4A7931C6.
Storage failures now latch off retries. bridge/check_storage.py is read-only.
Third boot received10 device interactions without test injection; fourth boot
retained lifetime10 with current presses0 and valid340-byte readback. Reopening
serial also returned that same state. Nonzero count controlled-restart PASS.
Gesture timing, markers, mode controls, physical power loss and screen QA pending.
One serial silence interval after boot3 recovered after controlled reset; root
cause unknown. Do not label that intermittent communication issue fixed.
Agent copy is a separate user-facing task; it must not flash or open this port.
Older direction and release notes below are historical.

## Active direction: pixel companion (2026-09-22)

Worktree D:/tenfold-worktrees/pixel-firmware, branch codex/pixel-firmware.
Firmware main + bridge/companion.py are software-owned; pet_assets.h art-owned.
Product coordinates integration and exclusive COM9 lease. No flash write yet;
manual download mode requested after two handshake timeouts. Back up before write.
Current protocol and evidence: docs/pixel-companion/SOFTWARE.md. Old P0 below is
historical, not the current product. Android multi-commitment draft is retained
untouched in D:/tenfold-worktrees/android and is not part of this new release.

## Historical delivery entry

- Authoritative workspace: `D:\十日环`, branch `main`, repository `kimniniup-creator/tenfold-ai-hardware`.
- User guide: `docs/hackathon/DELIVERY.md`; release assets: `v0.1.0-hackathon`; frozen hashes: `docs/hackathon/release-manifest.json`.
- Three original printable EDCs are integrated. First print is Orbit-10 PLA smooth ring, calibration pieces before the five functional parts. Pin and press/spin are documented alternatives.
- Independent manufacturing verdict: `docs/hackathon/testing/original/MECHANICAL_VERDICT.md`. Final APK runtime verdict: `docs/hackathon/testing/original/APK_FINAL.md`. Independent acceptance: `docs/hackathon/acceptance/ORIGINAL_REVIEW.md`.
- O1 digital manufacturing passes; O2 local simulated Android paths pass. O3 real hardware and O4 physical printing remain untested. Source-state regression passed all 22 cases.
- Release `v0.1.0-hackathon` is published. All five asset hashes match the delivery manifest, and the published APK was downloaded and rehashed successfully.
- Final APK B960, the recommended Orbit ZIP and the complete delivery instructions were sent to Kim by the offerlai bot. All three messages were read back and verified. Delivery receipts stay local; private chat identifiers are not published.

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
