"""Read-only device storage diagnostics; never inject interactions or markers."""
import argparse
import json
import time
import serial

parser = argparse.ArgumentParser()
parser.add_argument('--port', required=True)
parser.add_argument('--output', required=True)
parser.add_argument('--seconds', type=float, default=5)
args = parser.parse_args()
if not 1 <= args.seconds <= 30:
    parser.error('seconds must be 1..30')
port = serial.Serial()
port.port, port.baudrate = args.port, 115200
port.timeout, port.write_timeout = .1, .5
port.dtr = port.rts = False
with open(args.output, 'x', encoding='utf-8') as output:
    port.open()
    try:
        end, next_request, index = time.monotonic()+args.seconds, 0, 0
        seen = set()
        requests = ('hello_request', 'storage_query', 'reading_query')
        while time.monotonic() < end:
            now = time.monotonic()
            if now >= next_request:
                port.write((json.dumps({'type': requests[index % 3]})+'\n').encode())
                index += 1
                next_request = now+.5
            raw = port.read_until(b'\n', 1024)
            try:
                value = json.loads(raw)
            except (ValueError, UnicodeError):
                continue
            if value.get('type') not in ('hello', 'storage_status', 'reading_status'):
                continue
            line = json.dumps(value, ensure_ascii=False)
            output.write(line+'\n')
            output.flush()
            if line not in seen:
                print(line, flush=True)
                seen.add(line)
    finally:
        port.close()
