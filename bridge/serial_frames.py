"""Bounded newline framing that retains partial USB reads across timeouts."""
import json


class JsonLines:
    def __init__(self, maximum=1024):
        self.maximum = maximum
        self.buffer = bytearray()
        self.discarding = False

    def feed(self, chunk):
        values = []
        for byte in chunk:
            if byte == 10:
                if not self.discarding and self.buffer:
                    try:
                        value = json.loads(self.buffer)
                        if isinstance(value, dict):
                            values.append(value)
                    except (ValueError, UnicodeError):
                        pass
                self.buffer.clear()
                self.discarding = False
            elif not self.discarding:
                if len(self.buffer) >= self.maximum:
                    self.buffer.clear()
                    self.discarding = True
                else:
                    self.buffer.append(byte)
        return values


def open_device(name, timeout=.05, write_timeout=.2):
    import serial
    port = serial.Serial()
    port.port, port.baudrate = name, 115200
    port.timeout, port.write_timeout = timeout, write_timeout
    port.dtr = port.rts = False
    port.open()
    return port
