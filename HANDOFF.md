# Tenfold P0 handoff

## Frozen Android candidate

- Source: `6e2bf0e`
- APK: `android-app/out-release/tenfold-p0.apk` (local build artifact)
- APK SHA-256: `B9604D2572CAD083F2A72D1D95628985EFBDB565E93FA4B9A3BBFB19C76259A8`
- Signing certificate SHA-256: `EB55B62C374F6A58766625F52B83BA34B17E8A6B8C0D2CB95257781884CB153A`

The APK remains offline-capable and truthfully labels simulation, USB, offline rules and real-Agent states. The API key is Android-Keystore encrypted and no live credential was used.

## Firmware

`python -m platformio run -d firmware` completes successfully with the exact locks in `firmware/platformio.ini`. The release ZIP is produced locally from `firmware/release/p0/`; binaries are release assets and intentionally ignored by Git. Use `flash.ps1` in its default update mode to preserve NVS. Factory mode is only for an empty board and overwrites NVS.

- Local release ZIP: `D:\tenfold-worktrees\android\firmware\release\tenfold-firmware-p0.zip`
- ZIP SHA-256: `B94F3C282D7B28B3E1650514505714A106FAE1E0C7D7D9BB32AA32C6F4E195C3`
- App image SHA-256: `C6089DDC3EF2F082D9E3E0A44B45B86472E9FDE68245AD6702E03A67BF00B6B3`
- Empty-board factory image SHA-256: `496149201D350A8A21982267FFCC91441801C5F319A4F238B6AD7B786DCC1CCB`

## Remaining physical acceptance

No M5StickS3 was available. A real-board owner must still verify first flash, Chinese screen layout, both physical key gestures, Android USB permission/CDC transport, persisted offer ACK, offline device event FIFO, disconnect/reconnect reconciliation and cold-boot time handshake. A live OpenAI-compatible Agent request also remains untested without a credential.
