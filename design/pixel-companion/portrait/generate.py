"""Offline 1-bit Tachikoma fan-art sprites and exact portrait screen examples.
Code-native raster assets: edit pixel geometry here, never generated header.
"""
from pathlib import Path
import json
from PIL import Image, ImageDraw, ImageFont

BASE = Path(__file__).resolve().parent
ROOT = BASE.parents[2]
STAGES = ['young', 'grown']
STATES = ['idle', 'press', 'rebound', 'happy', 'rest', 'mark']
TEXT = {'idle':'陪你读会儿','press':'陪你读会儿','rebound':'陪你读会儿',
        'happy':'陪你读会儿','rest':'安静陪着你','mark':'记下这一处'}

def sprite(stage, state, tick):
    im=Image.new('1',(32,32),0); d=ImageDraw.Draw(im)
    big=stage=='grown'
    shift=2 if state=='press' else (-2 if state=='rebound' else 0)
    shift+=-tick if state in ('idle','happy') else 0
    y=11+shift
    # Rear cockpit and antenna: stepped curved shell, offset right.
    if big:
        d.polygon([(17,y-6),(23,y-6),(26,y-3),(26,y+5),(17,y+5)],fill=1)
        d.line((23,y-4,24,y+2),fill=0)
        d.line((17,y-5,17,y-8),fill=1)
    else:
        d.polygon([(17,y-3),(21,y-3),(23,y-1),(23,y+5),(17,y+5)],fill=1)
    # Articulated legs and four wheels, attached to central chassis.
    if state=='rest':
        legs=[[(10,y+6),(7,y+9),(8,26)],[(21,y+6),(25,y+9),(24,26)],
              [(9,y+5),(5,y+8),(5,23)],[(23,y+5),(28,y+8),(28,23)]]
    else:
        reach=2 if big else 0
        low=26 if state!='rebound' else 24
        if state=='press': low=27
        legs=[[(10,y+5),(6,y+8),(4,low)],[(22,y+5),(26,y+8),(28,low)],
              [(10,y+4),(5-reach,y+5),(3-reach,22)],[(23,y+4),(27+reach,y+5),(29+reach,22)]]
    for line in legs:
        d.line(line,fill=1,width=2)
        xw,yw=line[-1]; d.rectangle((max(0,xw-1),yw-1,min(31,xw+1),yw+1),fill=1)
        d.point((xw,yw),fill=0)
    # Main spherical armor, black seam and a large lens.
    d.polygon([(11,y-2),(19,y-2),(23,y+1),(24,y+6),(21,y+9),(9,y+9),(7,y+6),(8,y+1)],fill=1)
    d.line((9,y+7,22,y+7),fill=0)
    if state=='rest' or (state=='press' and tick==0):
        d.line((11,y+2,16,y+2),fill=0,width=2)
    else:
        d.rectangle((11,y,16,y+5),fill=0)
        d.rectangle((12,y+1,15,y+4),fill=1)
        pupil=13+(tick if state=='idle' else 0)
        d.rectangle((pupil,y+2,pupil+1,y+3),fill=0)
    d.point((20,y+2),fill=0); d.point((9,y+5),fill=0)
    if big: d.line((19,y-1,22,y+1),fill=0)
    # Front manipulators distinct from locomotion legs.
    d.line([(12,y+9),(10,y+11),(12,y+12)],fill=1)
    d.line([(19,y+9),(21,y+11),(19,y+12)],fill=1)
    if state=='happy':
        d.line([(9,y+6),(5,y+3),(5,y-1)],fill=1,width=2)
        d.point((4,y-2),fill=1); d.point((6,y-2),fill=1)
        x=28 if tick else 2
        d.line((x-1,6,x+1,6),fill=1); d.line((x,5,x,7),fill=1)
    if state=='mark':
        d.rectangle((1,2,6,10),fill=1)
        d.polygon([(2,10),(3,8),(5,10)],fill=0)
        if tick: d.line([(8,3),(9,4),(11,2)],fill=1)
    if state=='rest' and tick: d.point((28,5),fill=1)
    if state=='rebound' and tick:
        d.line((9,29,12,29),fill=1); d.line((20,29,23,29),fill=1)
    if state=='press' and tick:
        d.point((1,28),fill=1); d.point((30,28),fill=1)
    return im

def packed(im):
    data=[]
    for y in range(32):
        for byte in range(4):
            data.append(sum((1<<(7-b)) if im.getpixel((byte*8+b,y)) else 0 for b in range(8)))
    return data

def font():
    import os
    path=os.environ.get('PET_PREVIEW_FONT',r'C:\Windows\Fonts\simsun.ttc')
    if not Path(path).exists(): raise RuntimeError('Set PET_PREVIEW_FONT to a Chinese font file')
    return ImageFont.truetype(path,12)

def screen(stage,state,im):
    s=Image.new('1',(135,240),0); d=ImageDraw.Draw(s); f=font()
    # text is drawn directly to a 1-bit surface, no antialiasing.
    def center(text,y):
        width=d.textbbox((0,0),text,font=f)[2]; d.text(((135-width)//2,y),text,font=f,fill=1)
    d.text((9,10),'阅读',font=f,fill=1)
    d.text((91,10),'本地',font=f,fill=1)
    d.line((9,29,125,29),fill=1)
    center('幼年机' if stage=='young' else '成长机',43)
    s.paste(im.resize((64,64),Image.Resampling.NEAREST),(35,74))
    center(TEXT[state],158)
    # Two business buttons only. Exact long-press owner belongs to firmware.
    d.line((9,209,125,209),fill=1)
    d.text((5,211),'轻按互动',font=f,fill=1)
    d.text((78,211),'侧键标记',font=f,fill=1)
    center('长按换模式',225)
    return s

def main():
    frames=[sprite(stage,state,tick) for stage in STAGES for state in STATES for tick in range(2)]
    names=[f'{stage}_{state}_{tick}' for stage in STAGES for state in STATES for tick in range(2)]
    for name,im in zip(names,frames): im.save(BASE/(name+'.png'))
    sheet=Image.new('RGB',(768,640),'black'); d=ImageDraw.Draw(sheet)
    for i,(name,im) in enumerate(zip(names,frames)):
        x=(i%6)*128; y=(i//6)*160
        sheet.paste(im.resize((128,128),Image.Resampling.NEAREST),(x,y))
        d.text((x+3,y+139),name,fill='white')
    sheet.save(BASE/'frames-preview.png')
    board=Image.new('1',(810,960),0)
    for a,stage in enumerate(STAGES):
        for b,state in enumerate(STATES):
            s=screen(stage,state,frames[a*12+b*2]); s.save(BASE/f'{stage}_{state}-screen.png')
            board.paste(s.resize((270,480),Image.Resampling.NEAREST),((b%3)*270,(b//3)*480))
        board.save(BASE/f'{stage}-portrait-preview.png')
    parts=['// Generated offline by design/pixel-companion/portrait/generate.py\n#pragma once\n#include <stdint.h>\nnamespace pet_portrait {\n',
      'enum class Stage : uint8_t { Young, Grown };\nenum class State : uint8_t { Idle, Press, Rebound, Happy, Rest, Mark };\n',
      'static constexpr uint8_t kWidth=32, kHeight=32, kFrameCount=24;\n',
      'static constexpr uint16_t kScreenWidth=135, kScreenHeight=240;\n',
      'static constexpr uint16_t kPalette[2]={0x0000,0xffff};\n',
      '// Each row: four bytes, MSB is leftmost pixel; 0 black, 1 white.\nstatic constexpr uint8_t kFrames[24][128]={\n']
    for name,im in zip(names,frames):
        parts.append('  { // '+name+'\n'); values=packed(im)
        for row in range(8): parts.append('    '+','.join('0x%02x'%v for v in values[row*16:(row+1)*16])+',\n')
        parts.append('  },\n')
    parts.append('''};
inline uint8_t frameIndex(Stage stage, State state, uint32_t elapsedMs) {
  const uint8_t s=static_cast<uint8_t>(stage), a=static_cast<uint8_t>(state);
  if(s>1 || a>5) return 0;
  uint8_t tick=0;
  switch(state) {
    case State::Idle: tick=(elapsedMs/850U)%2U; break;
    case State::Rest: tick=(elapsedMs/1400U)%2U; break;
    case State::Press: tick=elapsedMs>=80U; break;
    case State::Rebound: tick=elapsedMs>=100U; break;
    case State::Happy: tick=(elapsedMs/160U)%2U; break;
    case State::Mark: tick=elapsedMs>=160U; break;
  }
  return s*12U+a*2U+tick;
}
inline uint8_t pixel(uint8_t frame,uint8_t x,uint8_t y) {
  if(frame>=kFrameCount || x>=kWidth || y>=kHeight) return 0;
  return (kFrames[frame][y*4U+x/8U]>>(7U-x%8U))&1U;
}
} // namespace pet_portrait
''')
    (ROOT/'firmware/include/pet_portrait_assets.h').write_text(''.join(parts),encoding='utf-8')
    metadata={'screen':[135,240],'sprite':[32,32],'scale':2,'sprite_origin':[35,74],
      'stages':STAGES,'states':STATES,'frames':names,'palette':['#000000','#ffffff'],
      'wire_protocol_changed':False,'local_ui_copy':TEXT,'mode_candidates':['阅读','工作','健身','学习'],
      'growth_meaning':'累计互动产生的外观变化，不代表阅读进度、能力或健康状态',
      'growth_threshold':'由产品/软件定值；美术不读取或累计次数',
      'character':'Tachikoma fan art; not an original character',
      'preview':'design render; not a hardware screenshot'}
    (BASE/'manifest.json').write_text(json.dumps(metadata,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    print('Generated 24 1-bit frames (3072 bytes), 12 portrait screens and two preview boards.')

if __name__=='__main__': main()
