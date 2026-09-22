"""Explicit pet-only reset for reading-schema1 firmware; never erases flash."""
import argparse
import json
import time
import serial
from serial_frames import JsonLines


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--port', required=True)
    parser.add_argument('--confirm-reset', action='store_true', required=True)
    args = parser.parse_args()
    port = serial.Serial()
    port.port, port.baudrate = args.port, 115200
    port.timeout, port.write_timeout = .1, .5
    port.dtr = port.rts = False
    port.open()
    try:
        # One destructive request only. Never retry automatically on lost ACK.
        port.write(b'\n{"type":"pet_reset","confirm":true}\n')
        frames = JsonLines()
        deadline = time.monotonic() + 5
        while time.monotonic() < deadline:
            for value in frames.feed(port.read_until(b'\n', 1024)):
                if value.get('type') == 'pet_reset_ack':
                    print(json.dumps(value))
                    return 0 if value.get('ok') is True else 1
        print('No reset ACK. Query state before considering another reset.')
        return 2
    finally:
        port.close()


if __name__ == '__main__':
    raise SystemExit(main())
