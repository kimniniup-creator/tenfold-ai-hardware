"""Validate the built flash layout against the shipped P0 partition binary.

Usage: python firmware/tests/check_partition_upgrade.py OLD_PARTITIONS.bin
This checks build artifacts, not device execution or NVS power-loss behavior.
"""
from pathlib import Path
import struct
import sys


def partitions(path):
    entries = {}
    for offset in range(0, len(data := Path(path).read_bytes()), 32):
        block = data[offset:offset + 32]
        if len(block) != 32 or block[:2] != b'\xaa\x50':
            break
        _, kind, subtype, start, size, name, flags = struct.unpack('<HBBII16sI', block)
        entries[name.rstrip(b'\0').decode()] = (kind, subtype, start, size)
    assert entries, 'No partition records'
    return entries


root = Path(__file__).resolve().parents[1]
built = root / '.pio/build/m5stack-sticks3'
old = partitions(sys.argv[1])
new = partitions(built / 'partitions.bin')
for name in ['nvs', 'otadata', 'app0', 'app1', 'coredump']:
    assert new[name] == old[name], f'{name} changed: {old[name]} -> {new[name]}'
ordered = sorted(new.items(), key=lambda item: item[1][2])
for (left, a), (right, b) in zip(ordered, ordered[1:]):
    assert a[2] + a[3] <= b[2], f'Overlap: {left}, {right}'
assert new['tenfold_data'] == (1, 2, 0x670000, 0x60000)
assert new['tenfold_data'][2] == old['spiffs'][2]
assert new['spiffs'][2] + new['spiffs'][3] == old['spiffs'][2] + old['spiffs'][3]
assert (built / 'firmware.bin').stat().st_size < new['app0'][3]
assert ordered[-1][1][2] + ordered[-1][1][3] <= 8 * 1024 * 1024
print('PASS: P0 NVS/OTA/apps preserved, dedicated data partition disjoint, image fits 8 MB layout')
