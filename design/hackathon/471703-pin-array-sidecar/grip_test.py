"""Annotated grip trial schematic, NOT source pinboard geometry."""
from pathlib import Path
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.patches import Rectangle,Circle,Ellipse
from matplotlib.font_manager import FontProperties
ROOT=Path(__file__).resolve().parent
font=FontProperties(fname='C:/Windows/Fonts/msyh.ttc')
fig,ax=plt.subplots(figsize=(13,7),facecolor='#f5f6f1');ax.set_facecolor('#f5f6f1')
ax.add_patch(Rectangle((0,0),64,40,facecolor='#71818b',edgecolor='#33454f'))
ax.add_patch(Rectangle((-21,1),21,38,facecolor='#99a5a9',edgecolor='#33454f'))
ax.add_patch(Rectangle((8,8),48,24,facecolor='#e9a34b',edgecolor='#915721'))
for y in [9,31]:
 ax.add_patch(Rectangle((-29,y-5),29,10,facecolor='#c5d79c',edgecolor='#73834e'))
 for x in [-17,-6]:ax.add_patch(Circle((x,y),3.5,facecolor='#c5cbd0',edgecolor='#46535d'))
 ax.annotate('',xy=(-17,y),xytext=(-6,y),arrowprops={'arrowstyle':'<->','color':'#202020'})
ax.text(32,20,'M5 侧舱\n48×24×15 mm 包络',ha='center',va='center',fontproperties=font,fontsize=12)
ax.text(-11.5,20,'孔距 11 mm',ha='center',fontproperties=font,fontsize=10)
ax.plot([-23,-23],[-4,45],'--',color='#a75037')
ax.text(-24,47,'原框边界位置仅为夹具设计接口\n须实测确认有静态可夹区域',ha='center',fontproperties=font,fontsize=10,color='#a75037')
ax.add_patch(Ellipse((-65,20),25,34,fill=False,edgecolor='#8897a0',linestyle='--',linewidth=2))
ax.text(-65,20,'A\n掌托示意',ha='center',va='center',fontproperties=font,fontsize=12)
ax.annotate('拇指扫针阵\n必须在源实物上定位',xy=(-39,25),xytext=(-79,46),fontproperties=font,fontsize=10,arrowprops={'arrowstyle':'->','color':'#42596c'})
ax.annotate('B 握原把手翻转\n把手位置未知，实物确认',xy=(-41,5),xytext=(-77,-15),fontproperties=font,fontsize=10,arrowprops={'arrowstyle':'->','color':'#42596c'})
ax.text(-40,15,'← 原针板方向\n外形/范围未知\n未画原模型',ha='center',va='center',fontproperties=font,fontsize=10,color='#a75037')
ax.annotate('',xy=(-29,-6),xytext=(64,-6),arrowprops={'arrowstyle':'<->'})
ax.text(18,-10,'独立配件 93 mm（不含原针板）',ha='center',fontproperties=font,fontsize=11)
ax.set_xlim(-90,73);ax.set_ylim(-23,63);ax.set_aspect('equal');ax.axis('off')
ax.set_title('针板式 EDC｜握持试验示意（未实测）',fontproperties=font,fontsize=19,loc='left')
fig.text(.08,.04,'先做配件体量样 → 合法源针板校准 → 左右手各10分钟 / 50次翻转 → 记录干涉、疼痛、夹具位移；未通过不称口袋EDC。',fontproperties=font,fontsize=11)
fig.savefig(ROOT/'exports/grip-test.png',dpi=150,bbox_inches='tight')
