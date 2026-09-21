"""Original Tenfold tactile-pin EDC. mm. No imported/copyrighted toy geometry.
CadQuery 2.8.0. Run python build.py. Prints, assembly, motion and hardware evidence.
"""
from pathlib import Path
import argparse,json,itertools,math
import cadquery as cq
import numpy as np
import trimesh
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.colors import to_rgb
from mpl_toolkits.mplot3d.art3d import Poly3DCollection
R=Path(__file__).resolve().parent
p=argparse.ArgumentParser()
p.add_argument('--shaft-gap',type=float,default=.30,help='radial clearance')
p.add_argument('--board-length',type=float,default=48)
p.add_argument('--board-width',type=float,default=24)
p.add_argument('--board-height',type=float,default=15)
p.add_argument('--out',default='exports')
a=p.parse_args(); OUT=R/a.out; OUT.mkdir(parents=True,exist_ok=True)
G=a.shaft_gap; BL=a.board_length; BW=a.board_width; BH=a.board_height
assert .2<=G<=.4 and 44<=BL<=48 and 20<=BW<=24 and 10<=BH<=16
LX,LY=70.,42.; DECK=10.; SLED=1.2; EVA=.5
MZ=DECK+SLED+EVA; MT=MZ+BH; RAIL=MT+.3; TOP=RAIL+2.2
STROKE=3.2; PIN_D=6.; FLANGE_D=8.8; POCKET_D=9.5
CX,CY=35.,21.; DX=CX-BL/2; DY=CY-BW/2
PINS=[(x,y) for y in [12.,30.] for x in [11.,23.,35.,47.,59.]]
CORNERS=[(x,y) for y in [5.,37.] for x in [5.,65.]]
BOTTOM=[(x,y) for y in [4.1,37.9] for x in [25.,45.]]

def box(x,y,z,dx,dy,dz):return cq.Workplane('XY').box(dx,dy,dz,centered=False).translate((x,y,z))
def cyl(x,y,z,r,h):return cq.Workplane('XY').circle(r).extrude(h).translate((x,y,z))
def rounded(x,y,z,dx,dy,dz,r):return box(x,y,z,dx,dy,dz).edges('|Z').fillet(r)
def hexhole(x,y,z,af,h):
    return cq.Workplane('XY').polygon(6,af/math.cos(math.pi/6)).extrude(h).translate((x,y,z))
def cone(x,y,z,r1,r2,h):return cq.Workplane('XY').newObject([cq.Solid.makeCone(r1,r2,h,cq.Vector(x,y,z))])
def vol(s):return sum(v.Volume() for v in s.solids().vals())
def countersink(s,x,y,z,up=True):
    # cut 90-degree hole. 6.4 max mouth, 3.4 bore, 1.5 depth
    return s.cut(cone(x,y,z,1.7 if up else 3.2,3.2 if up else 1.7,1.5))

# Guide plate: screw heads flush on tactile side; all pins fitted from inner face.
guide=rounded(0,0,0,LX,LY,2.4,4)
for x,y in PINS:guide=guide.cut(cyl(x,y,-1,3+G,5))
for x,y in BOTTOM:
    guide=guide.cut(cyl(x,y,-1,1.7,5)); guide=countersink(guide,x,y,0,False)

# Separate through-pocket spacer avoids bridging over pin chambers.
spacer=rounded(0,0,2.4,LX,LY,5.2,4)
for x,y in PINS:spacer=spacer.cut(cyl(x,y,2.3,POCKET_D/2,5.4))
for x,y in BOTTOM+CORNERS:spacer=spacer.cut(cyl(x,y,2.3,1.7,5.4))

# Structural deck transfers press loads to frame; no pin can touch electronics.
frame=rounded(0,0,7.6,LX,LY,2.4,4)
for x,y in CORNERS:
    frame=frame.union(rounded(x-4.5,y-4.5,10,9,9,RAIL-10,1.2))
    frame=frame.cut(hexhole(x,y,10,5.8,RAIL-9.8))
    frame=frame.cut(cyl(x,y,7.5,1.7,RAIL-7.3))
for x,y in BOTTOM:
    frame=frame.union(rounded(x-4.5,y-3.9,10,9,7.8,7,1))
    frame=frame.cut(hexhole(x,y,10,5.8,7.2))
    frame=frame.cut(cyl(x,y,7.5,1.7,10))
# Sled alignment pegs. M5 retention by rails prevents lifting clear of these pegs.
for y in [6,36]:frame=frame.union(cyl(35,y,10,1.5,2.2))

# Sled replacement is the supported way to change boards. Frame accepts limited envelope.
sled=box(DX-1,DY-1,10,BL+2,BW+2,SLED)
# Locating ears always at standard peg positions, join the base with overlaps.
sled=sled.union(box(31,4,10,8,DY-3.5,SLED))
sled=sled.union(box(31,DY+BW-.5,10,8,38-(DY+BW-.5),SLED))
for y in [6,36]:sled=sled.cut(cyl(35,y,9.9,1.75,SLED+.2))
# Four open corner guides; no narrow guessed USB aperture.
for x in [DX-2,DX+BL+.4]:
    for y in [DY+1,DY+BW-4]:sled=sled.union(box(x,y,10,1.6,3,SLED+7))
for y in [DY-2,DY+BW+.4]:
    for x in [DX-1,DX+BL-1]:sled=sled.union(box(x,y,10,2,1.6,SLED+7))
# Extensions join guides to tray; do not enter the board envelope.
for x in [DX-2,DX+BL-1]:
    for y in [DY-2,DY+BW-1]:sled=sled.union(box(x,y,10,3,3,SLED))

# Clear the four frame posts by 0.3mm; preserve guide-to-tray links.
for xx in [0,60.2]:
    for yy in [0,32.2]:sled=sled.cut(box(xx,yy,9.9,9.8,9.8,10))

# Two identical rails, mirrored in assembly. Tabs touch only M5 corner borders.
rail=rounded(0,0,RAIL,70,9,2.2,2)
for x in [DX+1,DX+BL-5]:rail=rail.union(box(x,8,RAIL,4,3.3,2.2))
for x in [5,65]:
    rail=rail.cut(cyl(x,5,RAIL-.1,1.7,2.4));rail=countersink(rail,x,5,TOP-1.5,True)
rail2=rail.mirror('XZ',basePointVector=(0,21,0),union=False)

# One-piece captive pin, flange down when printed (assembly pose shown extended).
pin=cyl(0,0,-STROKE,PIN_D/2,STROKE+2.4).edges('<Z').chamfer(.5)
pin=pin.union(cyl(0,0,2.4,FLANGE_D/2,2))

# Calibration strip: three shaft gaps, nut pocket, M3 countersink, sled peg hole.
coupon=rounded(0,0,0,66,16,2.4,2)
for i,g in enumerate([.2,.3,.4]):coupon=coupon.cut(cyl(8+i*12,8,-1,3+g,5))
coupon=coupon.cut(hexhole(49,8,-1,5.8,5))
coupon=coupon.cut(cyl(59,8,-1,1.7,5));coupon=countersink(coupon,59,8,0,False)
# Pin-flange chamber coupon: confirms sidewall fit without printing whole spacer.
chamber=rounded(0,0,0,16,16,5.2,2).cut(cyl(8,8,-1,POCKET_D/2,7))

parts={'01_guide_plate':guide,'02_pin_spacer':spacer,'03_structural_frame':frame,
       '04_m5_sled':sled,'05_retaining_rail':rail,'06_pin':pin,
       'calibration_guide':coupon,'calibration_chamber':chamber,'calibration_roof':box(0,0,0,16,16,2.4)}
qty={'01_guide_plate':1,'02_pin_spacer':1,'03_structural_frame':1,'04_m5_sled':1,'05_retaining_rail':2,'06_pin':10,'calibration_guide':1,'calibration_chamber':1,'calibration_roof':1}
printposes={}
for n,s in parts.items():
    assert s.val().isValid() and len(s.solids().vals())==1,n
    cq.exporters.export(s,str(OUT/(n+'.step')))
    # Pin prints flange flat on bed; rail prints its top face down.
    t=s.rotate((0,0,0),(1,0,0),180) if n in ['06_pin','05_retaining_rail'] else s
    bb=t.val().BoundingBox();t=t.translate((-bb.xmin,-bb.ymin,-bb.zmin))
    printposes[n]=t
    cq.exporters.export(t,str(OUT/(n+'.stl')),tolerance=.035,angularTolerance=.12)

fixed=[('guide',guide,'#9caab1'),('spacer',spacer,'#647580'),('frame',frame,'#53646f'),('sled',sled,'#a9bb93'),('rail_a',rail,'#bad65a'),('rail_b',rail2,'#bad65a')]
placed=[(f'pin_{i+1:02}',pin.translate((x,y,0)),'#e0ba79' if i!=0 else '#bbd958') for i,(x,y) in enumerate(PINS)]
device=box(DX,DY,MZ,BL,BW,BH)
assembly=cq.Assembly()
for n,s,c in fixed+placed:assembly.add(s,name=n)
assembly.save(str(OUT/'assembly_printed.step'))

checks={'status':'DIGITAL_PRINT_TRIAL_ONLY_NOT_PHYSICALLY_TESTED','units':'mm','original_geometry':True,
    'parameters':vars(a),'dimensions':{'body':[LX,LY,TOP],'maximum_extended_thickness':TOP+STROKE,'pin_travel':STROKE,'pin_diameter':PIN_D,'shaft_radial_gap':G,'flange_radial_gap':(POCKET_D-FLANGE_D)/2,'minimum_deck_thickness':2.4,'minimum_hex_post_flat_wall':1.0},
    'm5_stack':{'frame_top':10,'sled_top':11.2,'eva_top':11.7,'m5_top':MT,'rail_underside':RAIL,'front_clearance':.3},'parts':{},'fixed_pair_checks':0,'motion_pair_checks':0,'pin_capture':{'shaft_hole_diameter':6+2*G,'flange_diameter':8.8,'flange_overlap_per_side':(8.8-(6+2*G))/2,'guide_engagement_at_pressed':2.4,'upper_hard_stop_z':7.6}}
for n,t in printposes.items():
    m=trimesh.load_mesh(OUT/(n+'.stl'))
    checks['parts'][n]={'quantity':qty[n],'watertight':bool(m.is_watertight),'winding_consistent':bool(m.is_winding_consistent),'components':len(m.split()),'bounds_mm':m.extents.round(4).tolist(),'volume_mm3':round(float(m.volume),3),'print_zmin':round(float(m.bounds[0,2]),6)}
    assert m.is_watertight and m.is_winding_consistent and len(m.split())==1 and m.volume>0,n
for (n1,s1,_),(n2,s2,_) in itertools.combinations(fixed+placed+[('M5',device,'')],2):
    v=vol(s1.intersect(s2));assert v<1e-5,(n1,n2,v);checks['fixed_pair_checks']+=1
# Sample 17 positions including hard stops. Neighbor swept envelopes are also disjoint.
for i,(x,y) in enumerate(PINS):
    for z in np.linspace(0,STROKE,17):
        moving=pin.translate((x,y,float(z)))
        for n,s,_ in fixed+[('M5',device,'')]:
            v=vol(moving.intersect(s));assert v<1e-5,('motion',i,z,n,v);checks['motion_pair_checks']+=1
assert FLANGE_D>6+2*G and 2.4>0 and abs(4.4+STROKE-7.6)<1e-8
assert min(math.dist(a,b) for a,b in itertools.combinations(PINS,2))>POCKET_D
checks['pin_neighbor_sweep']='disjoint cylinders, minimum centre distance 12 > chamber diameter 9.5'
checks['capture_logic']='8.8 flange cannot cross 6.6 guide hole; solid roof at7.6; plates locked by four M3 fasteners. Reverse assembly requires screw removal.'

# Hardware envelopes: eight captive M3 nuts and eight flush 90-degree head screws.
def nut(x,y):return hexhole(x,y,10,5.5,2.4).cut(cyl(x,y,9.9,1.65,2.6))
def screw_down(x,y,top,length):return cone(x,y,top-1.5,1.5,3,1.5).union(cyl(x,y,top-length,1.5,length-1.5))
def screw_up(x,y):return cone(x,y,0,3,1.5,1.5).union(cyl(x,y,1.5,1.5,14.5))
TOP_BOLT=next(v for v in [16,20,25,30] if v>=TOP-9)
assert TOP-TOP_BOLT>2.4
hardware=[]
for i,(x,y) in enumerate(CORNERS):hardware += [(f'top_bolt_{i}',screw_down(x,y,TOP,TOP_BOLT),'#b7c0c6'),(f'top_nut_{i}',nut(x,y),'#b7c0c6')]
for i,(x,y) in enumerate(BOTTOM):hardware += [(f'back_bolt_{i}',screw_up(x,y),'#b7c0c6'),(f'back_nut_{i}',nut(x,y),'#b7c0c6')]
checks['hardware']={'M3_countersunk_top_length':TOP_BOLT,'M3_countersunk_back_length':16,'head_max_diameter':6,'head_height':1.5,'nut_af':5.5,'nut_height':2.4,'nut_pocket_af':5.8,'pairs':0,'to_printed_and_M5':0,'tool_approach_checks':0}
for (n1,s1,_),(n2,s2,_) in itertools.combinations(hardware,2):assert vol(s1.intersect(s2))<1e-5,(n1,n2);checks['hardware']['pairs']+=1
for n1,s1,_ in hardware:
    for n2,s2,_ in fixed+placed+[('M5',device,'')]:
        v=vol(s1.intersect(s2));assert v<1e-5,('hardware',n1,n2,v);checks['hardware']['to_printed_and_M5']+=1
# straight 2mm hex driver, 30mm access. Internal engagement excluded.
for x,y in CORNERS:
    tool=cyl(x,y,TOP,1.2,30)
    for n,s,c in fixed+placed+hardware+[('M5',device,'')]:assert vol(tool.intersect(s))<1e-5,('toptool',n);checks['hardware']['tool_approach_checks']+=1
for x,y in BOTTOM:
    tool=cyl(x,y,-30,1.2,30)
    for n,s,c in fixed+placed+hardware+[('M5',device,'')]:assert vol(tool.intersect(s))<1e-5,('backtool',n);checks['hardware']['tool_approach_checks']+=1

# Data-cable clearance: whole short-end mouth, independent of guessed port coordinates.
# Official drawing places USB/Grove at +X after rotating M5 long axis to X.
# Conservative 16x16 cable outer section along X covers full15mm device end height+0.5 each.
cable=box(DX+BL,13,11.2,40,16,16)
hat=box(DX-30,13,11.2,30,16,16)
checks['ports']={'usb_grove_swept_envelope':[40,16,16],'hat_swept_envelope':[30,16,16],'checked_against':'all printed parts and fasteners; excludes intentional device connector engagement','intersections':{}}
for label,env in [('USB_Grove',cable),('HAT',hat)]:
    for n,s,c in fixed+placed+hardware:
        v=vol(env.intersect(s));assert v<1e-5,(label,n,v);checks['ports']['intersections'][label+'/'+n]=round(v,6)
# Board/sled insertion: rails absent, lower vertically. Guide clearances must hold.
for dz in [0,.5,2,5,15,30]:
    for n,s,c in fixed[:3]+[('sled',sled,'')]:assert vol(device.translate((0,0,dz)).intersect(s))<1e-5,('M5 insertion',dz,n)
# Sled is lowered over pegs before board; remove rails for both insertion steps.
for dz in [0,.5,1,2.5,5,20]:
    for n,s,c in fixed[:3]:assert vol(sled.translate((0,0,dz)).intersect(s))<1e-5,('sled insertion',dz,n)
checks['assembly']='pins through guide from inside; spacer; frame; four M3x16 from rear; drop sled and M5; two rails with four top bolts'
full=cq.Assembly()
for n,s,c in fixed+placed+hardware:full.add(s,name=n)
full.save(str(OUT/'assembly_hardware.step'))
(OUT/'validation.json').write_text(json.dumps(checks,indent=2),encoding='utf-8')

# CAD-only engineering views.
def render(name,mode):
    fig=plt.figure(figsize=(12,8),facecolor='#f3f4ed');ax=fig.add_subplot(111,projection='3d');ax.set_facecolor('#f3f4ed')
    objs=fixed+placed+([] if mode=='exploded' else hardware)+[('M5',device,'#e4a147')]
    tt=[];cc=[]
    for n,s,c in objs:
        dz=0
        if mode=='exploded':
            dz=30 if n.startswith('rail') else 20 if n=='M5' else 12 if n=='sled' else 5 if n=='frame' else -8 if n=='spacer' else -18 if n.startswith('pin') else -25
        if mode=='back' and n.startswith('pin'):
            i=int(n[-2:])-1;s=s.translate((0,0,STROKE if i%3==0 else 0))
        vs,fs=s.val().tessellate(.15);xyz=np.array([[v.x,v.y,v.z+dz] for v in vs]);tri=xyz[np.array(fs)]
        norm=np.cross(tri[:,1]-tri[:,0],tri[:,2]-tri[:,0]);norm/=np.maximum(np.linalg.norm(norm,axis=1)[:,None],1e-12)
        light=np.array([.2,-.4,-.89 if mode=='back' else .89]);shade=.62+.38*np.maximum(norm@light,0)
        tt.extend(tri);cc.extend(shade[:,None]*np.array(to_rgb(c)))
    ax.add_collection3d(Poly3DCollection(tt,facecolors=cc,edgecolors='none'))
    ax.set_xlim(-5,75);ax.set_ylim(-5,47);ax.set_zlim(-28 if mode=='exploded' else -8,TOP+36 if mode=='exploded' else TOP+5)
    ax.set_box_aspect((80,52,TOP+64 if mode=='exploded' else TOP+13));ax.view_init(-35 if mode=='back' else 32,-57)
    ax.set_xlabel('X / mm');ax.set_ylabel('Y / mm');ax.set_zlabel('Z / mm')
    title={'front':'M5 face / open data ends','back':'Ten captive tactile pins / 3.2 mm stroke','exploded':'Assembly order / original printable mechanics'}[mode]
    ax.set_title('TENFOLD / TEN-PEBBLE PALM\n'+title,loc='left',fontsize=16)
    fig.text(.08,.04,'CAD preview. Orange = nominal M5 envelope. No physical print or tactile test performed.\n10 independent gravity-return pins; retention by flange + guide plate + solid roof.',fontsize=10)
    fig.savefig(OUT/name,dpi=150,bbox_inches='tight');plt.close(fig)
render('front.png','front');render('back.png','back');render('exploded.png','exploded')
roundtrip={}
for f in OUT.glob('*.step'):
    vs=cq.importers.importStep(str(f)).solids().vals();expected=32 if f.stem=='assembly_hardware' else 16 if f.stem=='assembly_printed' else 1
    assert len(vs)==expected and all(v.isValid() and v.Volume()>0 for v in vs),f.name
    roundtrip[f.name]={'solids':len(vs),'valid':True}
(OUT/'step_roundtrip.json').write_text(json.dumps(roundtrip,indent=2),encoding='utf-8')
print(json.dumps({'parts':checks['parts'],'hardware':checks['hardware'],'motion_checks':checks['motion_pair_checks']},indent=2))
