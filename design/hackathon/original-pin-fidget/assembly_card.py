"""Chinese assembly orientation card, coordinates derived from default CAD."""
from pathlib import Path
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.patches import Rectangle,Circle,FancyArrowPatch
from matplotlib.font_manager import FontProperties
R=Path(__file__).resolve().parent;fnt=FontProperties(fname='C:/Windows/Fonts/msyh.ttc')
f,axs=plt.subplots(1,3,figsize=(16,7),facecolor='#f3f4ed',gridspec_kw={'width_ratios':[1.2,1.2,.8]})
for a in axs:a.set_facecolor('#f3f4ed');a.set_aspect('equal');a.axis('off')
a=axs[0];a.add_patch(Rectangle((0,0),70,42,fc='#657984',ec='#33444e'))
for i,(x,y) in enumerate([(x,y) for y in [12,30] for x in [11,23,35,47,59]]):
 a.add_patch(Circle((x,y),3,fc='#b8d54f' if i==0 else '#e1b56c',ec='#57452b'));a.text(x,y,str(i+1),ha='center',va='center',fontsize=8)
for x in [25,45]:
 for y in [4.1,37.9]:a.add_patch(Circle((x,y),3,fc='#c6ccd0',ec='#53646f'))
a.annotate('',xy=(11,22),xytext=(59,22),arrowprops={'arrowstyle':'<->','color':'#fff','lw':2})
a.text(35,50,'背面：拇指扫过 2×5 圆头',ha='center',fontproperties=fnt,fontsize=14)
a.text(35,-9,'按入 → 翻转 / 轻晃复位\n不是弹簧点击或日珠锁存',ha='center',va='top',fontproperties=fnt,fontsize=12)
a.set_xlim(-5,75);a.set_ylim(-20,58)
a=axs[1];a.add_patch(Rectangle((0,0),70,42,fc='#d4dcd4',ec='#54606a'))
a.add_patch(Rectangle((11,9),48,24,fc='#e3a24a',ec='#7a581f'))
for y in [0,33]:a.add_patch(Rectangle((0,y),70,9,fc='#b8d54f',ec='#7a8d36'))
for x in [5,65]:
 for y in [5,37]:a.add_patch(Circle((x,y),3,fc='#c6ccd0',ec='#53646f'))
a.text(35,21,'M5 原机屏幕朝上\n仅示包络，不是屏幕开窗尺寸',ha='center',va='center',fontproperties=fnt,fontsize=10)
a.text(35,50,'正面：双压条捕获电子件',ha='center',fontproperties=fnt,fontsize=14)
a.annotate('HAT\n-X',xy=(11,21),xytext=(-7,21),ha='right',fontproperties=fnt,fontsize=10,arrowprops={'arrowstyle':'->'})
a.annotate('USB / Grove\n+X',xy=(59,21),xytext=(77,21),ha='left',fontproperties=fnt,fontsize=10,arrowprops={'arrowstyle':'->'})
a.text(35,-9,'先锁紧机械三层，再放内托和M5\n前后螺钉均从对应外侧插入',ha='center',va='top',fontproperties=fnt,fontsize=12)
a.set_xlim(-18,91);a.set_ylim(-20,58)
a=axs[2]
for x in [-8,3.3]:a.add_patch(Rectangle((x,0),4.7,2.4,fc='#9caab1',ec='#52616a'))
for x in [-8,4.75]:a.add_patch(Rectangle((x,2.4),3.25,5.2,fc='#647580',ec='#52616a'))
a.add_patch(Rectangle((-8,7.6),16,2.4,fc='#53646f'))
a.add_patch(Rectangle((-3,-3.2),6,5.6,fc='#ddb779'))
a.add_patch(Rectangle((-4.4,2.4),8.8,2,fc='#ddb779'))
a.add_patch(Rectangle((-3,0),6,5.6,fill=False,ls='--',ec='#a35031'))
a.add_patch(Rectangle((-4.4,5.6),8.8,2,fill=False,ls='--',ec='#a35031'))
a.annotate('',xy=(10,5.6),xytext=(10,2.4),arrowprops={'arrowstyle':'<->'})
a.text(11,4,'3.2 mm',va='center',fontsize=10)
a.text(0,14,'单销剖面：法兰捕获',ha='center',fontproperties=fnt,fontsize=14)
a.text(0,-5,'虚线为按到底\n上方2.4mm实体板隔离电子件\n校准腔必须先打',ha='center',va='top',fontproperties=fnt,fontsize=11)
a.set_xlim(-12,22);a.set_ylim(-12,18)
f.suptitle('十粒掌盘｜先校准，再机械，最后装电子',fontproperties=fnt,fontsize=22,x=.05,ha='left')
f.text(.05,.08,'整机本体70×42×29.2 mm；销全伸出最大厚32.4 mm。橙色M5包络48×24×15 mm。\n此卡来自CAD尺寸；未实物打印、未验证摩擦/手感/真实按键操作。软件功能以USER_JOURNEY与最终固件为准。',fontproperties=fnt,fontsize=12)
f.subplots_adjust(top=.83,bottom=.22,wspace=.4)
f.savefig(R/'exports/assembly_card.png',dpi=150,bbox_inches='tight')
