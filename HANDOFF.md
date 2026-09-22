# Tenfold P0 handoff

## Active direction: pixel companion (2026-09-22)

Worktree D:/tenfold-worktrees/pixel-firmware, branch codex/pixel-firmware.
Firmware main + bridge/companion.py are software-owned; pet_assets.h art-owned.
Product coordinates integration and exclusive COM9 lease. No flash write yet;
manual download mode requested after two handshake timeouts. Back up before write.
Current protocol and evidence: docs/pixel-companion/SOFTWARE.md. Old P0 below is
historical, not the current product. Android multi-commitment draft is retained
untouched in D:/tenfold-worktrees/android and is not part of this new release.

## Final delivery entry

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
