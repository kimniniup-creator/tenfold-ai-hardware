"""Independent parametric M5 sidecar. No MakerWorld geometry is reproduced.
Run: python build.py --frame-thickness 8 --frame-land 6
Frame parameters are UNMEASURED examples, never source dimensions.
"""
from pathlib import Path
import argparse, json, itertools
import cadquery as cq
import trimesh
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.colors import to_rgb
from mpl_toolkits.mplot3d.art3d import Poly3DCollection

ROOT=Path(__file__).resolve().parent
p=argparse.ArgumentParser()
p.add_argument('--frame-thickness',type=float,default=8)
p.add_argument('--frame-land',type=float,default=6)
a=p.parse_args()
T=a.frame_thickness; LAND=a.frame_land
assert 4<=T<=14 and 4<=LAND<=10, 'Example clamp parameter range only'
OUT=ROOT/'exports'; OUT.mkdir(exist_ok=True)

def box(x,y,z,dx,dy,dz):
    return cq.Workplane('XY').box(dx,dy,dz,centered=False).translate((x,y,z))
def hole(x,y,z,r,h):
    return cq.Workplane('XY').circle(r).extrude(h).translate((x,y,z))
def volume(s):
    return sum(v.Volume() for v in s.solids().vals())

# Device axes: X=48 long, Y=24 wide, Z=15 thick. 0.5 mm lateral allowance.
# Device lower corner (8,8,3); nominal front surface Z=18.
base=box(0,0,0,64,40,2.5).edges('|Z').fillet(3)
# 0.5 mm total EVA+adhesive occupies Z=2.5..3.0, already included in device Z=3.
# Four open corner guides; sides and ends have large uninterrupted access.
for x in [3,61]:
    for y in [3,37]:
        base=base.union(hole(x,y,2.5,3,15.8))
        base=base.cut(hole(x,y,-1,1.2,22)) # M2.5 pilot: qualify by coupon
# x guides close to device ends only near corners
for x in [5.5,56.5]:
    for y in [7,29]:
        base=base.union(box(x,y,2.5,2,4,14.8))
for y in [5.5,32.5]:
    for x in [8,52]:
        base=base.union(box(x,y,2.5,4,2,14.8))
# Mounting flange extends away from the M5 envelope; two clamp screws per station.
base=base.union(box(-10,1,0,12,38,3))
for y in [9,31]:
    for x in [-7,-2]:
        base=base.cut(hole(x,y,-1,1.7,5))

# Cover supported by corner columns; oversized central opening + only corner tabs.
cover=box(0,0,18.3,64,40,2).edges('|Z').fillet(3)
cover=cover.cut(box(7.5,7.5,18,49,25,3))
# Large side cutouts keep top rim from shading M5 side keys/ports.
for x in [0,58.5]:
    cover=cover.cut(box(x,12,18,5.5,16,3))
for y in [0,34.5]:
    cover=cover.cut(box(14,y,18,36,5.5,3))
for x in [7.5,53.5]:
    for y in [7.5,29.5]:
        cover=cover.union(box(x,y,18.3,3,3,2))
for x in [3,61]:
    for y in [3,37]:
        cover=cover.cut(hole(x,y,18,1.45,4))

# Removable clamp lower shoe, two M3 bolts through flange (x=-7,-2).
# Edge stop at x=-12; frame extends toward negative X, NEVER toward M5.
# Sole contacts only LAND mm of static outer rim. Pad=0.5 each side.
clamp_x=-12-LAND
lower=box(clamp_x,-5,0,12+LAND,10,3)
# Vertical edge stop, establishes board edge at X=-12.
lower=lower.union(box(-12,-5,3,2,10,T+.6))
for x in [-7,-2]:
    lower=lower.cut(hole(x,0,-1,1.7,6))
# Upper shoe bridge closes over flange with M3 through bolts/nuts.
upper=box(clamp_x,-5,T+4,12+LAND,10,3)
for x in [-7,-2]:
    upper=upper.cut(hole(x,0,T+3,1.7,5))
# Static example rim coupon: NOT an original-model proxy and NOT exported.
frame_coupon=box(clamp_x,-5,3.5,LAND,10,T)
parts={'sidecar_base':base,'corner_cover':cover,'lower_clamp':lower,'upper_clamp':upper}
for name,s in parts.items():
    assert s.val().isValid(),name
    cq.exporters.export(s,str(OUT/(name+'.step')))
    # STL exports rest each part flat on build plate.
    z=s.val().BoundingBox().zmin
    cq.exporters.export(s.translate((0,0,-z)),str(OUT/(name+'.stl')),tolerance=.05,angularTolerance=.15)
# Assembly lower clamps must sit below flange (top=-0.3), separated for pads.
clamp_offset=-3.3
assembled=[('base',base,'#526776'),('cover',cover,'#b4d75a')]
for i,y in enumerate([9,31]):
    assembled += [(f'lower{i}',lower.translate((0,y,clamp_offset)),'#73828d'),
                  (f'upper{i}',upper.translate((0,y,clamp_offset)),'#cad7a9')]
device=box(8,8,3,48,24,15)
assembly=cq.Assembly()
for name,s,col in assembled:
    assembly.add(s,name=name)
assembly.save(str(OUT/'independent_adapter_assembly.step'))

checks={'status':'PROTOTYPE_NOT_SOURCE_FITTED','source_geometry_available':False,
        'parameters':{'frame_thickness_UNMEASURED':T,'static_land_UNMEASURED':LAND},
        'device_envelope_mm':[48,24,15], 'parts':{},'intersections_mm3':{},
        'cover_device_axial_clearance_mm':.3,'nominal_lateral_clearance_mm':.5,
        'source_pin_motion_check':'BLOCKED: source STL and pin travel unavailable'}
for name,s in parts.items():
    m=trimesh.load_mesh(OUT/(name+'.stl'))
    checks['parts'][name]={'watertight':bool(m.is_watertight),'winding_consistent':bool(m.is_winding_consistent),
        'components':len(m.split()),'bounds_mm':m.extents.round(3).tolist(),'volume_mm3':round(m.volume,2)}
    assert m.is_watertight and m.is_winding_consistent and len(m.split())==1 and m.volume>0,name
for (n1,s1,_),(n2,s2,_) in itertools.combinations(assembled+[('M5_envelope',device,'')],2):
    v=volume(s1.intersect(s2)); checks['intersections_mm3'][n1+' / '+n2]=round(v,6)
    assert v<1e-5,(n1,n2,v)
# Clamp parallel closure sweeps only against example static coupon, not original pinboard.
# 0.5 mm pads per side; board can be installed sideways with screws removed.
checks['m5_z_stack_mm']={'rigid_floor_top':2.5,'eva_total_thickness':0.5,'eva_bottom':2.5,'eva_top':3.0,'device_bottom':3.0,'device_top':18.0,'cover_underside':18.3,'clearance_with_pad':0.3}
assert abs((2.5+0.5)-device.val().BoundingBox().zmin)<1e-8
assert abs((cover.val().BoundingBox().zmin-device.val().BoundingBox().zmax)-0.3)<1e-8
checks['clamp_contact']='0.5 mm pad allowance each side for parameterized rectangular rim ONLY'
checks['clamp_closure_sweep']={'samples':11,'travel_mm':0.4,'scope':'independent clamp only; original pinboard absent'}
for y in [9,31]:
    for d in np.linspace(0,.4,11):
        moving=upper.translate((0,y,clamp_offset-float(d)))
        for fixed in [base,lower.translate((0,y,clamp_offset))]:
            assert volume(moving.intersect(fixed))<1e-5
checks['assembly_insertion']='Cover removed: M5 lowers vertically; clamps assembled with bolts removed'
(OUT/'validation.json').write_text(json.dumps(checks,indent=2),encoding='utf8')

# Engineering previews from actual CAD tessellation, no AI imagery or fake pin array.
def render(filename,explode=False):
    fig=plt.figure(figsize=(12,8),facecolor='#f5f6f1'); ax=fig.add_subplot(111,projection='3d')
    ax.set_facecolor('#f5f6f1')
    objects=assembled+[('M5 envelope',device,'#ee9a41')]
    alltris=[]; allcolors=[]
    for name,s,col in objects:
        dz=0
        if explode:
            if name=='cover':dz=32
            elif name=='M5 envelope':dz=16
            elif name.startswith('upper'):dz=18
            elif name.startswith('lower'):dz=-12
        verts,faces=s.val().tessellate(.15)
        xyz=np.array([[v.x,v.y,v.z+dz] for v in verts]); tris=xyz[np.array(faces)]
        normals=np.cross(tris[:,1]-tris[:,0],tris[:,2]-tris[:,0])
        normals=normals/np.maximum(np.linalg.norm(normals,axis=1)[:,None],1e-12)
        shade=.65+.35*np.maximum(normals@np.array([.2,-.4,.89]),0)
        alltris.extend(tris);allcolors.extend(shade[:,None]*np.array(to_rgb(col)))
    ax.add_collection3d(Poly3DCollection(alltris,facecolor=allcolors,edgecolor='none',zsort='average'))
    ax.set_xlim(-25,70);ax.set_ylim(-5,45);ax.set_zlim(-18,58 if explode else 28)
    ax.set_box_aspect((95,50,76 if explode else 46));ax.view_init(elev=28,azim=-58)
    ax.set_xlabel('X / mm');ax.set_ylabel('Y / mm');ax.set_zlabel('Z / mm')
    ax.set_title('TENFOLD / PIN-ARRAY SIDECAR\n'+('Exploded CAD assembly' if explode else 'CAD assembly — M5 nominal envelope'),loc='left',fontsize=16)
    fig.text(.08,.055,'GREEN: cover / GREY: independent adapter / ORANGE: M5 envelope\nOriginal pinboard NOT shown: download requires login; clamp dimensions are unmeasured examples.',fontsize=10)
    fig.savefig(OUT/filename,dpi=160,bbox_inches='tight');plt.close(fig)
render('assembly.png');render('exploded.png',True)
roundtrip={}
for f in OUT.glob('*.step'):
    solids=cq.importers.importStep(str(f)).solids().vals()
    roundtrip[f.name]={'solids':len(solids),'valid':all(s.isValid() for s in solids),'positive_volume':all(s.Volume()>0 for s in solids)}
    assert roundtrip[f.name]['valid'] and roundtrip[f.name]['positive_volume']
    assert len(solids)==(6 if 'assembly' in f.name else 1)
(OUT/'step_roundtrip.json').write_text(json.dumps(roundtrip,indent=2))
print(json.dumps(checks,indent=2))
