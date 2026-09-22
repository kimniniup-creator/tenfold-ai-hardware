# Multi-commitment firmware

Protocol 1 remains compatible. `hello` now reports `multi_cycle: true`, `capacity: 10`, and `cycle_count`. Each commitment has independent command/revision/day, completion fact, host sequence, device sequence, and up to eight unsynchronized device events. No card is silently replaced when capacity is full (`capacity_full`).

`offer` upserts by `cycle_id` and optionally accepts `goal_short` (240 UTF-8 bytes). `query` with `cycle_id` selects that commitment and returns its status and original queued events. A missing commitment returns `status`, the requested `cycle_id`, `device_id`, `protocol: 1`, `persisted: false`, `state: MISSING`, and `last_seq: 0`. Host events, device event acknowledgments, and time confirmation route by `cycle_id`, including after another commitment has been selected. The phone must query/synchronize every local commitment; queues are replayed per queried card.

When locked, click A to switch resident commitments. Hold A+B one second, release, use A to choose completion or sealing, then hold B 1.5 seconds to confirm. A serial selection cancels an open physical confirmation window to prevent applying it to the wrong card. The display shows the card position, goal, current action, and day. Completion requires per-card time confirmation after reboot; sealing remains available offline.

## Storage and upgrade

All cards are one checksummed, double-slot NVS **blob** snapshot, with a verified active marker. Legacy single-card snapshots are read from the original `nvs` partition and migrated on first boot. Original NVS remains intact. No physical board migration has been tested.

The original Tenfold P0 8 MB layout has app0 at `0x10000` (size `0x330000`) and app1 at `0x340000` (size `0x330000`). This firmware preserves those boundaries, original NVS (`0x9000`, size `0x5000`), OTA data (`0xe000`, size `0x2000`), and coredump (`0x7f0000`). It allocates `tenfold_data` at `0x670000`, size `0x60000`, from the previously unused Tenfold SPIFFS partition; remaining SPIFFS starts at `0x6d0000`.

Build from the repository root: `python -m platformio run -d firmware`.

For a verified Tenfold P0 layout booting app0, upgrade with segmented writes (replace COM7):

```powershell
python -m esptool --chip esp32s3 --port COM7 write_flash 0x8000 firmware/.pio/build/m5stack-sticks3/partitions.bin 0x10000 firmware/.pio/build/m5stack-sticks3/firmware.bin
```

Do not use the old app-only release script for the initial multi-card upgrade: the new partition table is required. Do not apply this command to an unrelated layout, a device with user SPIFFS data, or an unknown OTA boot slot. Verify/back up first; changing SPIFFS boundaries makes its old contents unavailable. No automatic erase or factory reset is performed. Subsequent updates on this layout may write only the active application slot. Downgrading to P0 does not expose the multi-card data.

Capacity is ten resident commitments; this version does not delete individual cards. Real USB transport, physical buttons, flash migration, and power-loss behavior require board acceptance. A successful compiler/linker run does not establish those results.
