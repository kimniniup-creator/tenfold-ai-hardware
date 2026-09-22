import unittest
from unittest.mock import patch
import reset_pet


class Port:
    def __init__(self, ack):
        self.ack = ack
        self.writes = []
        self.closed = False

    def open(self):
        assert self.dtr is False and self.rts is False

    def write(self, value):
        self.writes.append(value)
        return len(value)

    def read_until(self, *args):
        return self.ack

    def close(self):
        self.closed = True


class ResetTests(unittest.TestCase):
    def test_explicit_confirmation_required(self):
        with patch('sys.argv', ['reset_pet', '--port', 'FAKE']), patch('reset_pet.serial.Serial') as serial:
            with self.assertRaises(SystemExit):
                reset_pet.main()
            serial.assert_not_called()

    def test_ack_and_error_never_retry(self):
        for ok, result in [('true', 0), ('false', 1)]:
            port = Port(('{"type":"pet_reset_ack","ok":'+ok+'}\n').encode())
            with patch('sys.argv', ['reset_pet', '--port', 'FAKE', '--confirm-reset']), patch('reset_pet.serial.Serial', return_value=port):
                self.assertEqual(reset_pet.main(), result)
            self.assertEqual(port.writes, [b'\n{"type":"pet_reset","confirm":true}\n'])
            self.assertTrue(port.closed)
