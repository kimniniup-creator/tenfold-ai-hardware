# Pixel companion software

New direction, separate from historical Tenfold release. Original 32×32 sprites
render at 2× with Chinese text on a 240×135 canvas.

## Run

Build: `python -m platformio run -d firmware`.
Dependency: `python -m pip install pyserial`.
Bridge: `python bridge/companion.py --port COM9` (rediscover actual port).
Without credentials: explicit local rules. Optional environment variables:
`PET_API_URL` full HTTPS chat/completions URL, `PET_API_KEY`, `PET_MODEL`.
DeepSeek additionally uses `PET_DISABLE_THINKING=1`. Never commit credentials.

## Interaction / protocol 2

A press edge counts once, holding does not repeat. Hold duration accumulates
each loop, split at window boundaries. Quiet preserves press/rebound interaction.
B toggles quiet and increments epoch to invalidate outstanding responses.
Quiet preference persists after two seconds without another toggle.

NDJSON: RX cap 512 bytes, 128-byte loop budget. Single TX frame cap 768 bytes,
nonblocking partial drain. `hello_request` reports chip, board enum, dimensions,
build, random boot session, epoch, quiet and physical press total; no input injection.
`rhythm` contains session, epoch, window, duration_ms, presses, held_ms,
mean_interval_ms, quiet, candidate. Windows normally 10s; an outstanding request
may extend a window to 15s. Three presses nominate a response, minimum 60s cooldown.
Telemetry may be dropped under backpressure; no replay or persistent history.
Only successful enqueue consumes candidate cooldown. Disconnected local play
does not depend on telemetry. Reply must match session/epoch/window, arrive in
15s and only one is accepted. Quiet rejects every reply.

Bridge keeps dedup and cooldown across reconnects in the same process. A single
request subprocess enforces an 8s wall-clock deadline including DNS and headers;
timed-out child is killed and reaped. Host drops replies after 12s. Device cooldown
survives USB reconnect, but not full power restart.

Both ends accept only actions blink/happy/rest and these exact phrases:
我在。 / 我在，陪你待会儿。 / 嗯，接住了。 / 慢慢来就好。 /
安静待着，也很好。
Agent selects a reviewed phrase and action, not free-form advice. Rest is an
animation, never a quiet-mode mutation. Screen uses two lines, no truncated phrase.

## Evidence / remaining hardware gate

PlatformIO compile passed. Real provider through `respond` returned source=agent,
action=rest, text=我在，陪你待会儿。 for synthetic rhythm (4 presses/10s,
600ms held/900ms mean interval). This is not physical-button evidence.
Original design preview was viewed; it is NOT a device photo.
COM9 VID:PID 303A:832B enumerated, default/USB reset handshakes both returned
Write timeout. No flash write occurred. Product task requested manual download
mode using official instructions: https://docs.m5stack.com/en/core/StickS3

Before write: identify chip, back up full flash to ignored `.delivery`, hash it,
inspect partition table. Never erase all flash. Backup may contain private data,
must not upload. Physical screen, buttons, offline play and board-Agent loop
remain NOT_TESTED. Software holds the exclusive port lease via product task.
