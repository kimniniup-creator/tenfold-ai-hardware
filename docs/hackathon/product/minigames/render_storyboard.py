"""Static 135x240 wireframes; existing character art is reused unchanged."""
from pathlib import Path
import os
from PIL import Image, ImageDraw, ImageFont
ROOT=Path(__file__).resolve().parents[4]
OUT=Path(__file__).parent
FONT=os.environ.get('PET_PREVIEW_FONT', 'C:/Windows/Fonts/simsun.ttc')
f=ImageFont.truetype(FONT,12)
heading=ImageFont.truetype(FONT,20)
pet=Image.open(ROOT/'design/pixel-companion/portrait/young_idle_0.png').convert('RGB')
grown=Image.open(ROOT/'design/pixel-companion/portrait/grown_idle_0.png').convert('RGB')
board=Image.new('RGB',(1490,1610),'#202020'); bd=ImageDraw.Draw(board)
bd.text((20,10),'五款小游戏 · 静态布局 / 非实板 · 每屏135×240，展示放大2倍',font=heading,fill='white')
names=['一起跳绳','羽毛球对打','敲敲回声','接住书签','一起修桥']
frames=[('准备','命中','回书'),('来球','选路·二阶','回书'),('它先敲','轮到你','回书'),('它递来','接住了','回书'),('换方向','试走','回书')]
for g in range(5):
 for step in range(3):
  im=Image.new('RGB',(135,240),'black'); d=ImageDraw.Draw(im)
  def text(x,y,s):
   assert d.textbbox((x,y),s,font=f)[2]<=135,(g,step,s)
   d.text((x,y),s,font=f,fill='white')
  text(5,5,names[g]);text(108,5,str(0 if step==2 else [36,40,40,36,48][g]-step*3))
  d.line((4,26,130,26),fill='white');text(5,32,frames[g][step])
  if step==2:
   im.paste(grown if g==4 else pet,(51,70));text(13,123,'一起玩过一会儿')
   d.rectangle((7,151,127,172),outline='white');text(20,155,'回到书里');text(20,179,'再玩一次')
   text(6,207,'A 选择 B 确认');text(6,223,'静置8秒回书')
  else:
   if g==0:
    im.paste(pet.resize((64,64),Image.Resampling.NEAREST),(35,90-step*8))
    d.arc((8,66,125,178),0 if step==0 else 150,180 if step==0 else 350,fill='white',width=2)
    d.line((29,161,106,161),fill='white',width=2);text(30,178,'○ ○ ○' if step==0 else '配合上了')
    text(5,205,'A 合拍 B 慢拍')
   elif g==1:
    im.paste(grown if step else pet,(51,51));d.rectangle((15,91,120,181),outline='white')
    d.line((15,112,120,112),fill='white',width=2)
    for y in range(95,163,8):d.line((35,y,35,y+3),fill='white')
    d.ellipse((32,140,38,146),fill='white');d.rectangle((24,168,47,172),fill='white')
    text(5,184,'来回 3' if step==0 else '回左 / 回右');text(5,205,'A 左  B 右')
   elif g==2:
    im.paste(pet,(51,64));d.rectangle((18,125,51,145),outline='white',width=2);d.rectangle((83,125,116,145),outline='white',width=2)
    d.line((34,108,34,120),fill='white',width=2)
    for x in [42,61,80]:d.rectangle((x,165,x+12,177),outline='white')
    text(5,205,'看完 A左 B右')
   elif g==3:
    im.paste(pet,(51,59))
    for x in [35,100]:
     for y in range(103,166,8):d.line((x,y,x,y+3),fill='white')
    d.rectangle((32,126 if step==0 else 157,38,136 if step==0 else 167),fill='white');d.line((23,173,47,173),fill='white',width=3)
    text(5,183,'接住 4 / 12');text(5,205,'A 左  B 右')
   else:
    for n,(x,y) in enumerate([(20,66),(80,106),(20,146)]):
     d.rectangle((x,y,x+28,y+28),outline='white');d.line((x+14,y,x+14,y+14,x+28,y+14),fill='white',width=3)
     text(x-12,y,str(n+1))
    d.line((48,80,110,80,110,120),fill='white');d.line((80,120,60,120,60,160,48,160),fill='white')
    im.paste(grown,((83,151) if step==0 else (80,66)));text(5,205,'A 旋转 B 放下' if step==0 else '它在试走')
   text(5,223,'双键长按 回书')
  x=20+g*294;y=45+step*520
  # Nearest-neighbor 2x display; native frames are also exported.
  board.paste(im.resize((270,480),Image.Resampling.NEAREST),(x,y))
  im.save(OUT/f'wire-{g+1}-{step+1}.png')
board.save(OUT/'storyboard.png')
print('15 native 135x240 frames; storyboard',board.size)
