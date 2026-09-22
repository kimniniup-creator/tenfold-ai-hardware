"""Check deliverable geometry, state differentiation and offline reproducibility."""
import hashlib
import subprocess
import sys
from pathlib import Path
from PIL import Image
import generate

base=Path(__file__).resolve().parent
paths=list(base.glob('*.png'))+[base/'palette.json',generate.ROOT/'firmware/include/pet_assets.h']
before={p:hashlib.sha256(p.read_bytes()).hexdigest() for p in paths}
subprocess.run([sys.executable,str(base/'generate.py')],check=True)
assert all(hashlib.sha256(p.read_bytes()).hexdigest()==h for p,h in before.items())
pixels=[]
for name in generate.NAMES:
    im=Image.open(base/(name+'.png'))
    assert im.size==(32,32) and im.info['transparency']==0
    data=bytes(im.get_flattened_data()); assert max(data)<8
    pixels.append(data)
assert len(set(pixels))==10, 'Each animation frame must be distinct'
for p in base.glob('*-screen.png'): assert Image.open(p).size==(240,135)
print('PASS: 10 distinct frames, valid palette/transparency, exact screen geometry, deterministic outputs.')
