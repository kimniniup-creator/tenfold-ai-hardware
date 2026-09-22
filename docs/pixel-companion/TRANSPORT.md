# USB reconnect repair, 2026-09-22

## Reproduction and diagnosis

Original app repeatedly stopped returning even raw bytes after a host closed and
reopened COM10. A buffered diagnostic reader ruled out partial-JSON parsing as
the sole cause. DTR=false/true (RTS=false throughout) both worked before failure.
Without any board reset, one old boot later recovered and accumulated real
input, so permanent application deadlock was not established.

Repro: five3-second query/reopen cycles, eight seconds of hello requests without
reading, five seconds resumed reading, then another reopen. Original returned
only stale hello frames on resumed reading and zero raw bytes after reopening.
Local evidence: `.delivery/reconnect-baseline-pressure.ndjson`.

The application had one pending TX frame with no expiration, rejected all new
responses while that frame remained, discarded queued state on `!Serial`, and
advanced by requested rather than accepted write length. A full/stalled HWCDC
ring could therefore indefinitely block fresh query replies. Setting HWCDC's
timeout from0 to1 alone did NOT fix the reproduction (local log
`.delivery/reconnect-timeout1-round1.ndjson`). Keep1 to avoid the separate known
unsigned-underflow hazard in the pinned core; see
https://github.com/espressif/arduino-esp32/issues/12634.

## Fix

- No application `Serial` boolean gate on queue admission/draining.
- Each pending frame expires after250ms; bounded HWCDC flush kicks transmission
  and can drop stale queued bytes. This is transport recovery, not board reset.
- Advance only by Serial.write's returned length;1ms nonzero driver timeout.
- Prefix newline resynchronizes after an abandoned partial frame. Host retains
  partial frames across timeouts, bounds memory, skips invalid/oversize frames.
- Companion opens with DTR/RTS false before opening, matching diagnostic tools.
- Read-only queries can echo request_id(max32 bytes); transport_query exposes
  uptime/loop/accepted-byte/pending/expiration diagnostics, never state mutation.

This protocol provides refreshed snapshots, not reliable delivery of every
telemetry frame. Deliberately abandoned frames are expected under a non-reading
host. Durable interaction/marker state is not discarded with TX telemetry.

## Verified result

Two rounds, each five reopens plus8-second non-reader stress, resume-reading and
reopen-after-pressure, passed hello/storage/transport *fresh request IDs*.
Same boot session throughout both rounds; no reset or injected buttons.
Lifetime188 and marks4 unchanged, storage readback valid340 bytes, board26,
135x240/display_ready. Loop count advanced throughout; maximum observed loop gap
21ms. Expired-frame counter advanced under stress. Resume-reading discarded4
malformed stale fragments per round then delivered fresh valid frames; final
reopen had zero malformed frames. This is expected frame resynchronization,
not a claim of lossless telemetry. Physical gestures during saturation were not
injected or separately verified.

- `.delivery/reconnect-bounded-round1.ndjson`
- `.delivery/reconnect-bounded-round2.ndjson`
- `python bridge/reconnect_probe.py --port COM10 --output NEW_LOG_PATH`
- Eleven host tests PASS, including fragmented UTF-8/timeouts, oversize recovery,
  pre-open port flags and firmware safety guards; actual firmware build PASS.
- App716256 bytes, SHA256
  `09E04A4FC38973040FF2F95B46A32685D8BD785192460565992AEE122CE10B11`.
  App-only update; matched bootloader unchanged.

This closes the reproduced backpressure/reopen stall in this tested build. It
does not claim every USB cable/host/power-disconnect scenario is tested. The
precise internal HWCDC interrupt race was not captured through JTAG (driver
unavailable; no driver changes were made).
