import json
import unittest
from unittest.mock import patch
from serial_frames import JsonLines, open_device


class SerialFrameTests(unittest.TestCase):
    def test_timeout_and_split_utf8_keep_partial_frame(self):
        wire = (json.dumps({'type': 'hello', 'text': '你好'}, ensure_ascii=False)+'\n').encode()
        frames = JsonLines()
        actual = []
        for byte in wire:
            actual += frames.feed(bytes([byte]))
            self.assertEqual(frames.feed(b''), [])
        self.assertEqual(actual, [{'type': 'hello', 'text': '你好'}])

    def test_oversize_and_bad_frame_resynchronize(self):
        frames = JsonLines(32)
        self.assertEqual(frames.feed(b'x'*40), [])
        self.assertLessEqual(len(frames.buffer), 32)
        self.assertEqual(frames.feed(b'\nBAD\n\n{"ok":true}\n'), [{'ok': True}])

    def test_port_flags_are_set_before_open(self):
        with patch('serial.Serial') as constructor:
            port = constructor.return_value
            def check():
                self.assertFalse(port.dtr)
                self.assertFalse(port.rts)
                self.assertEqual(port.port, 'TEST_PORT')
            port.open.side_effect = check
            self.assertIs(open_device('TEST_PORT'), port)
            constructor.assert_called_once_with()


if __name__ == '__main__':
    unittest.main()
