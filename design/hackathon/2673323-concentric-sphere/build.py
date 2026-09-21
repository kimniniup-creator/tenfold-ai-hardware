"""Original removable accessory; no MakerWorld geometry. Units: mm."""
import argparse, json, pathlib
import numpy as np
import trimesh as tm
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d.art3d import Poly3DCollection

p=argparse.ArgumentParser(); p.add_argument('--ball-diameter',type=float,default=60); p.add_argument('--output',type=pathlib.Path); a=p.parse_args()
assert 50<=a.ball_diameter<=80, 'Accessory design range: 50..80 mm; source diameter unknown'
out=a.output or pathlib.Path(__file__).parent; out.mkdir(parents=True,exist_ok=True); R=a.ball_diameter/2; cx=R+20
def box(size,pos):
    m=tm.creation.box(size); m.apply_translation(pos); return m
def cyl(r,h,pos):
    m=tm.creation.cylinder(r,h,sections=96); m.apply_translation(pos); return m
def union(parts): return tm.boolean.union(parts,engine='manifold')
def cut(m,parts): return tm.boolean.difference([m,*parts],engine='manifold')
def sphere(r,pos):
    m=tm.creation.uv_sphere(radius=r,count=[48,64]); m.apply_translation(pos); return m

# Shallow palm saucer + side electronics frame. Ball is removable for unrestricted play.
base=union([cyl(R-3,3,[0,0,1.5]), cyl(R-5,7,[0,0,6.5]),
            box([cx+15,24,3],[(cx+15)/2,0,1.5]),box([31,56,3],[cx,0,1.5]),
            box([27.2,50.8,4],[cx,0,5])])
base=cut(base,[sphere(R+.6,[0,0,R+3]),box([24.8,48.8,28],[cx,0,17])])
# Corner posts sit outside the device envelope; screw holes are vertical and fully open.
posts=[(cx+sx*15,sy*27) for sx in [-1,1] for sy in [-1,1]]
base=union([base,*[cyl(3.2,17.5,[x,y,11.75]) for x,y in posts]])
holes=[cyl(1.7,40,[x,y,15]) for x,y in posts]
slots=[box([9,3,20],[0,sy*(R-8),5]) for sy in [-1,1]]
base=cut(base,holes+slots)
# Two open ends leave USB/Grove/Hat and reset access, with long-side access between posts.
frame=union([box([3.2,56,2.5],[cx+sx*13.1,0,21.75]) for sx in [-1,1]]+
            [box([31,3.2,2.5],[cx,sy*26,21.75]) for sy in [-1,1]]+
            [cyl(3.2,2.5,[x,y,21.75]) for x,y in posts])
frame=cut(frame,holes)
device=box([24,48,15],[cx,0,10.5]) # floor z=3, top=18; insert 2mm foam => top20
device.apply_translation([0,0,2])
ball=sphere(R,[0,0,R+3])
parts={'palm_cradle':base,'retaining_frame':frame}
report={'source_ball_diameter_verified':False,'ball_diameter_assumed_mm':2*R,
 'supported_parameter_range_mm':[50,80], 'm5_envelope_mm':[48,24,15],
 'm5_xy_clearance_per_side_mm':.4,'m5_top_gap_mm':.5,
 'ball_seat_nominal_radial_clearance_mm':.6,'physical_print_tested':False,'parts':{}}
for name,m in parts.items():
    assert m.is_watertight and m.is_volume and len(m.split())==1
    m.export(out/(name+'.stl'))
    report['parts'][name]={'watertight':bool(m.is_watertight),'positive_volume':bool(m.is_volume),
      'connected_components':len(m.split()),'bounds_mm':m.bounds.tolist(),'volume_mm3':float(m.volume)}
def intersection_volume(x,y):
    m=tm.boolean.intersection([x,y],engine='manifold'); return float(m.volume) if len(m.vertices) else 0.
report['interference_mm3']={name:intersection_volume(m,device) for name,m in parts.items()}
report['interference_mm3']['base_frame']=intersection_volume(base,frame)
report['interference_mm3']['ball_base']=intersection_volume(ball,base)
report['interference_mm3']['ball_frame']=intersection_volume(ball,frame)
report['interference_mm3']['ball_m5']=intersection_volume(ball,device)
assert max(report['interference_mm3'].values())<.01,report
# Spherical swept envelope is rotation invariant; this checks envelope only, never original internals.
report['rotation_check']='360-degree envelope invariant; original nested layers NOT verified'
(out/'verification.json').write_text(json.dumps(report,indent=2),encoding='utf8')
def render(explode=False):
    fig=plt.figure(figsize=(12,8),facecolor='#f1f2ef'); ax=fig.add_subplot(projection='3d')
    objs=[(base,'#737f83',1),(frame.copy(),'#b1c735',1),(device.copy(),'#d87826',.8),(ball.copy(),'#9eadae',.14)]
    if explode:
        objs[1][0].apply_translation([0,0,45]); objs[2][0].apply_translation([0,0,24]); objs[3][0].apply_translation([0,0,38])
    for m,color,alpha in objs:
        c=Poly3DCollection(m.triangles,facecolor=color,edgecolor='none',alpha=alpha); ax.add_collection3d(c)
    ax.set(xlim=(-R-5,cx+23),ylim=(-R-8,R+8),zlim=(0,2*R+48 if explode else 2*R+8),xlabel='X / mm',ylabel='Y / mm',zlabel='Z / mm')
    ax.set_box_aspect((cx+R+28,2*R+16,2*R+(48 if explode else 8))); ax.view_init(28,-65)
    ax.set_title(('EXPLODED' if explode else 'ASSEMBLY')+f' | removable concentric-ball palm carrier\nTransparent sphere = assumed {2*R:g} mm envelope, NOT source geometry',fontsize=13)
    fig.text(.06,.025,'Grey: original palm cradle | Lime: screw retaining frame | Orange: M5 48 x 24 x 15\nSource ball not supplied. Foam, strap and screws omitted. No physical fit claim.',fontsize=10)
    fig.savefig(out/('exploded.png' if explode else 'assembly.png'),dpi=170); plt.close(fig)
render(); render(True)
print(json.dumps(report,indent=2))
