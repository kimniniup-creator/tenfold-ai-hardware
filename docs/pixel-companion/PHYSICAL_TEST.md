# Physical test procedure — pending download-mode action

Software is sole port owner. Do not run bridge and capture simultaneously.

1. Identify chip/8MB flash with esptool after successful ROM handshake. Read all
   flash into ignored `.delivery`; verify length/hash and retain local recovery.
   Inspect partition table at 0x8000, active app and boot configuration before
   selecting write offsets. No full erase. Do not reuse assumed old offsets.
2. Flash only verified required ranges; capture tool output and SHA. Reset,
   enumerate new serial port by USB identity. Query protocol-2 hello and verify
   chip, board enum, width=240,height=135 and fresh session.
3. Run `python bridge/capture_device.py --port COM9 --seconds 90` while the owner
   performs the sequence once: A three taps; A hold 3 seconds then release;
   B quiet; A once while quiet; B return. Record owner's visual observations.
   Total press delta must be five, not repeated during hold; epoch increases two.
   Raw capture is ignored and not uploaded without review.
4. Stop capture, run configured bridge. After cooldown ask three A taps, record
   rhythm and source=agent selected response and owner's screen observation.
   B quiet during a request must keep quiet even if the request completes.
5. Disconnect USB and press A/B on battery. Only owner observation proves this
   result; previous serial logs cannot prove unplugged screen behavior.
6. Reconnect and query status, then test restart for quiet preference after its
   two-second save delay. Release lease to independent tester only after all
   serial processes exit.

No synthetic key-injection endpoint exists. Asset preview is not a board photo;
compile, protocol, real-provider, physical-input and visual evidence stay separate.
