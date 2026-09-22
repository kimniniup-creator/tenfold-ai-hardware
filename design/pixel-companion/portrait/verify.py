"""Validate generated delivery, including C++ packed-data to PNG equality."""
from pathlib import Path
import hashlib
import re
import subprocess
import sys
from PIL import Image, ImageDraw
import generate as g

base=Path(__file__).resolve().parent
header=g.ROOT/'firmware/include/pet_portrait_assets.h'
paths=list(base.glob('*.png'))+[base/'manifest.json',header]
before={p:hashlib.sha256(p.read_bytes()).hexdigest() for p in paths}
subprocess.run([sys.executable,str(base/'generate.py')],check=True)
assert all(hashlib.sha256(p.read_bytes()).hexdigest()==h for p,h in before.items())
array=header.read_text(encoding='utf-8').split('kFrames[40][128]={')[1].split('};')[0]
raw=[int(h,16) for h in re.findall(r'0x([0-9a-f]{2})',array)]
assert len(raw)==5120
frames=[]
for idx,(stage,state,t) in enumerate(g.frame_specs()):
    im=Image.open(base/f'{stage}_{state}_{t}.png')
    assert im.size==(32,32) and im.mode=='1'
    frames.append(im.tobytes())
    for y in range(32):
        for x in range(32):
            bit=(raw[idx*128+y*4+x//8]>>(7-x%8))&1
            assert bit==bool(im.getpixel((x,y)))
assert len(set(frames))==40
for path in base.glob('*-screen.png'):
    im=Image.open(path); assert im.size==(135,240) and im.mode=='1'
f=g.font(); d=ImageDraw.Draw(Image.new('1',(135,240)))
for text,x,y in [('轻按照料',5,211),('侧键标记',78,211),('长侧键换模式',31,225)]:
    box=d.textbbox((x,y),text,font=f)
    assert box[0]>=0 and box[2]<=135 and box[1]>=0 and box[3]<=240,box
assert max(len(t) for t in g.TEXT.values())<=12
for name in ['lock-icon.png','unlock-icon.png','recent-marks-icon.png']:
    assert Image.open(base/name).size==(8,8)
print('PASS: 40 distinct 1-bit frames; C++/PNG pixel parity; portrait geometry; footer bounds; icons; deterministic generation.')
