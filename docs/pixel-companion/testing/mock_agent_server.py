"""Loopback-only controllable HTTP fixture for bridge tests; never records headers/secrets."""
import argparse, json, time
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path


def main():
    p = argparse.ArgumentParser()
    p.add_argument('--port', type=int, default=18763)
    p.add_argument('--status', type=int, default=200)
    p.add_argument('--delay', type=float, default=0)
    p.add_argument('--response-file', type=Path, required=True)
    p.add_argument('--record', type=Path, required=True)
    a = p.parse_args()
    response = a.response_file.read_bytes()
    a.record.parent.mkdir(parents=True, exist_ok=True)

    class Handler(BaseHTTPRequestHandler):
        def log_message(self, *_):
            pass

        def do_POST(self):
            length = int(self.headers.get('Content-Length', '0'))
            if not 0 <= length <= 65536:
                self.send_error(413)
                return
            raw = self.rfile.read(length)
            # Synthetic fixtures only. Header values, credentials and payload text are not persisted.
            try:
                body = json.loads(raw)
                keys = sorted(body) if isinstance(body, dict) else []
            except ValueError:
                keys = []
            entry = {'monotonic': time.monotonic(), 'path': self.path,
                     'body_bytes': len(raw), 'json_top_level_keys': keys,
                     'response_status': a.status, 'delay_seconds': a.delay}
            with a.record.open('a', encoding='utf-8') as stream:
                stream.write(json.dumps(entry) + '\n')
            time.sleep(max(0, a.delay))
            try:
                self.send_response(a.status)
                self.send_header('Content-Type', 'application/json')
                self.send_header('Content-Length', str(len(response)))
                self.end_headers()
                self.wfile.write(response)
            except (BrokenPipeError, ConnectionResetError, ConnectionAbortedError):
                pass

    server = ThreadingHTTPServer(('127.0.0.1', a.port), Handler)
    print(json.dumps({'listening': '127.0.0.1', 'port': a.port}), flush=True)
    server.serve_forever()


if __name__ == '__main__':
    main()
