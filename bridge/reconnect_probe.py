"""Bounded read-only USB reconnect/backpressure regression, with frame buffering."""
import argparse
import json
import time
import serial


def open_port(name, dtr=False):
    port = serial.Serial()
    port.port, port.baudrate = name, 115200
    port.timeout, port.write_timeout = .02, .2
    port.dtr, port.rts = dtr, False
    port.open()
    return port


def exchange(port, seconds=3):
    end, next_query, index = time.monotonic()+seconds, 0, 0
    buffer = bytearray()
    records, raw_bytes, bad_frames = [], 0, 0
    sent_ids = set()
    types = ('hello_request', 'storage_query', 'transport_query')
    while time.monotonic() < end:
        now = time.monotonic()
        if now >= next_query:
            request_id = str(time.monotonic_ns())
            sent_ids.add(request_id)
            port.write((json.dumps({'type': types[index % 3], 'request_id': request_id})+'\n').encode())
            next_query, index = now+.2, index+1
        chunk = port.read(1024)
        raw_bytes += len(chunk)
        buffer.extend(chunk)
        while b'\n' in buffer:
            line, _, tail = buffer.partition(b'\n')
            buffer = bytearray(tail)
            if not line.strip():
                continue
            try:
                value = json.loads(line)
                if isinstance(value, dict):
                    records.append(value)
            except (ValueError, UnicodeError):
                bad_frames += 1
        if len(buffer) > 4096:
            buffer.clear()
            bad_frames += 1
    fresh = [item for item in records if item.get('request_id') in sent_ids]
    return dict(raw_bytes=raw_bytes, bad_frames=bad_frames,
                fresh_types=sorted({item.get('type') for item in fresh}),
                partial_bytes=len(buffer), records=records)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--port', required=True)
    parser.add_argument('--output', required=True)
    parser.add_argument('--cycles', type=int, default=5)
    parser.add_argument('--backpressure', type=float, default=8)
    args = parser.parse_args()
    if not 1 <= args.cycles <= 10 or not 0 <= args.backpressure <= 15:
        parser.error('cycles1..10, backpressure0..15')
    with open(args.output, 'x', encoding='utf-8') as log:
        failures, sessions = [], set()
        def report(phase, value):
            required = {'hello', 'storage_status', 'transport_status'}
            passed = required.issubset(value['fresh_types'])
            if not passed:
                failures.append(phase)
            sessions.update(item['session'] for item in value['records']
                            if item.get('type') == 'hello')
            row = dict(phase=phase, passed=passed, **value)
            log.write(json.dumps(row, ensure_ascii=False)+'\n')
            log.flush()
            snapshots = {item.get('type'): item for item in value['records']}
            print(json.dumps(dict(phase=phase, raw_bytes=value['raw_bytes'],
                                  passed=passed,
                                  bad_frames=value['bad_frames'],
                                  fresh_types=value['fresh_types'],
                                  snapshots=snapshots), ensure_ascii=False), flush=True)
        for cycle in range(args.cycles):
            with open_port(args.port, dtr=bool(cycle % 2)) as port:
                report(f'reopen-{cycle}', exchange(port))
            time.sleep(.25)
        if args.backpressure:
            with open_port(args.port) as port:
                # Only status requests; never inject input or mutate stored state.
                end = time.monotonic()+args.backpressure
                while time.monotonic() < end:
                    port.write(b'{"type":"hello_request"}\n')
                    time.sleep(.03)
                report('resume-reading', exchange(port, 5))
            with open_port(args.port) as port:
                report('reopen-after-pressure', exchange(port, 5))
        if len(sessions) != 1:
            failures.append('boot-session-changed-or-missing')
        print(json.dumps(dict(passed=not failures, failures=failures,
                              boot_sessions=len(sessions))), flush=True)
        if failures:
            raise SystemExit(1)


if __name__ == '__main__':
    main()
