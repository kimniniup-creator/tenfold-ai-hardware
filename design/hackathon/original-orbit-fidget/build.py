"""Original Orbit-10: fully captive rotor and modular whole-device M5StickS3 cradle.
CadQuery analytic source. Millimetres. No third-party model geometry redistributed.
Python 3.12; pip install -r requirements.txt; python build.py
"""
import argparse, json, math, pathlib
import cadquery as cq
import numpy as np
import trimesh as tm

ap=argparse.ArgumentParser()
ap.add_argument('--output',type=pathlib.Path)
ap.add_argument('--radial-gap',type=float,default=.5)
ap.add_argument('--reference',type=pathlib.Path)
ap.add_argument('--skip-motion',action='store_true')
args=ap.parse_args()
OUT=args.output or pathlib.Path(__file__).parent
OUT.mkdir(parents=True,exist_ok=True)
GAP=args.radial_gap
assert .35<=GAP<=.6
POSTS=[(sx*16.5,sy*20) for sx in [-1,1] for sy in [-1,1]]
def cylinder(r,h,x=0,y=0,z=0,d=(0,0,1)):
    return cq.Solid.makeCylinder(r,h,cq.Vector(x,y,z),cq.Vector(*d))
def box(w,l,h,x=0,y=0,z=0):
    return cq.Solid.makeBox(w,l,h,cq.Vector(x-w/2,y-l/2,z))
def sphere(r,x=0,y=0,z=0):
    return cq.Solid.makeSphere(r,cq.Vector(x,y,z),angleDegrees1=-90,angleDegrees2=90)
def fuse(*ss):
    return ss[0].fuse(*ss[1:]).clean() if len(ss)>1 else ss[0]
def difference(s,*cuts):
    return s.cut(*cuts).clean()
def hexagon(af,h,x,y,z):
    return cq.Workplane('XY').polygon(6,af/math.cos(math.pi/6)).extrude(h).val().translate((x,y,z))
def holes(z=-1,h=40): return [cylinder(1.7,h,x,y,z) for x,y in POSTS]
def footprint(z,h,clearance=0):
    c=clearance
    return fuse(box(27.2+2*c,51.2+2*c,h,z=z),
        *[box(33+2*c,6.4+2*c,h,y=y,z=z) for y in [-20,20]],
        *[cylinder(3.2+c,h,x,y,z) for x,y in POSTS])

# Base journal remains continuous over the rotor bearing height, except the detent bore.
base=fuse(cylinder(32.5,3),cylinder(30,6.8,z=3),footprint(9.8,.2))
base=difference(base,*holes(),*[hexagon(5.9,2.6,x,y,-.01) for x,y in POSTS],
                cylinder(1.65,8.3,22,0,6.4,d=(1,0,0)))

# Free plain-bearing rotary joint, chamfered lower entry; ten scallops and optional pockets.
rotor=difference(cylinder(37.5,6,z=3.4),cylinder(30+GAP,8,z=2.4),
    cq.Solid.makeCone(30+GAP+.8,30+GAP,.8,cq.Vector(0,0,3.4)))
for i in range(10):
    ang=math.radians(i*36)
    rotor=difference(rotor,cylinder(2.4,8,38*math.cos(ang),38*math.sin(ang),2.4),
        sphere(1.8,29.8*math.cos(ang),29.8*math.sin(ang),6.4))

# The top capture ring is itself trapped by four outward tabs on the removable cradle.
capture=difference(cylinder(32.5,2.2,z=9.8),footprint(9,4,.3))
cradle=fuse(footprint(10,2),*[cylinder(3.2,17.5,x,y,10) for x,y in POSTS],
    *[box(1.2,46,2.5,x=x,z=12) for x in [-13,13]],
    *[box(4,6,1.5,x=sx*20,y=sy*20,z=12) for sx in [-1,1] for sy in [-1,1]])
cradle=difference(cradle,*holes())
lid=fuse(*[box(2.8,52,2.5,x=x,z=27.5) for x in [-12.9,12.9]],
    *[box(28.6,1.4,2.5,y=y,z=27.5) for y in [-25.3,25.3]],
    *[cylinder(3.2,2.5,x,y,27.5) for x,y in POSTS])
lid=difference(lid,*holes(),*[cq.Solid.makeCone(1.7,3.2,1.5,cq.Vector(x,y,28.5)) for x,y in POSTS])

# Calibration before the full print: three radial fits and the actual 3.3 mm detent bore.
gauge=fuse(box(22,44,2),cylinder(6,6,y=-11,z=2),box(18,16,6,y=11,z=2))
gauge=difference(gauge,*[cylinder(r,18,x=x,y=2,z=5,d=(0,1,0)) for x,r in [(-6,1.6),(0,1.65),(6,1.7)]])
parts={'01_base':base,'02_rotor':rotor,'03_capture_ring':capture,
       '04_m5_cradle':cradle,'05_face_frame':lid,'calibration_base':gauge}
for gap in [.2,.35,.5]:
    parts[f'calibration_ring_{round(gap*100):03d}']=difference(cylinder(9,5),cylinder(6+gap,7,z=-1))

def mesh(s):
    vs,fs=s.tessellate(.035,.12)
    m=tm.Trimesh(np.array([v.toTuple() for v in vs]),np.asarray(fs),process=True)
    m.merge_vertices(); m.fix_normals(); return m
report={'units':'mm','physical_print_tested':False,'radial_gap_per_side':GAP,
        'axial_gap_each':.4,'capture_overlap_radial':2.5-GAP,'rotor_degrees':[0,360],
        'screw':'4 x M3x30 countersunk + 4 x M3 nut AF5.5 H2.4',
        'optional_detent':'1 x ball D3 + spring OD2.5 wire0.3 L8, solid height <=3',
        'parts':{},'pair_interference_mm3':{}}
meshes={}
for name,s in parts.items():
    print('Export/check',name,flush=True)
    assert s.isValid() and len(s.Solids())==1,name
    cq.exporters.export(s,str(OUT/(name+'.step')))
    m=mesh(s); assert m.is_watertight and m.is_volume and len(m.split())==1,name
    m.export(OUT/(name+'.stl')); meshes[name]=m
    # Analytic STEP roundtrip in OCCT, not just file creation.
    reimport=cq.importers.importStep(str(OUT/(name+'.step'))).val()
    assert reimport.isValid() and abs(reimport.Volume()-s.Volume())<.01,name
    report['parts'][name]={'watertight':bool(m.is_watertight),'components':len(m.split()),
      'volume_mm3':s.Volume(),'bounds_mm':m.bounds.tolist(),'step_roundtrip_valid':True,
      'print_translation_z':-float(m.bounds[0,2]),'quantity':1}
main=list(parts)[:5]
def iv(a,b):
    s=a.intersect(b); return sum(x.Volume() for x in s.Solids()) if s.Solids() else 0.
for i,n in enumerate(main):
    for n2 in main[i+1:]:
        v=iv(parts[n],parts[n2]);report['pair_interference_mm3'][n+' / '+n2]=v
        assert v<.01,(n,n2,v)

device=box(24,48,15,z=12)
report['m5_box_interference_mm3']={n:iv(parts[n],device) for n in main}
assert max(report['m5_box_interference_mm3'].values())<.01,report['m5_box_interference_mm3']
# Full open end access, avoiding dependence on tiny guessed port holes.
access={'usb_grove_combined':box(16,30,14.5,y=39.1,z=12.5),
 'hat_end':box(22,25,10,y=-36.6,z=13),
 'side_button_left':box(15,15,10,x=-19.6,z=16),
 'side_button_right':box(15,15,10,x=19.6,z=16),
 'reset_tool_left':cylinder(1,18,-12.1,-15.5,20,d=(-1,0,0)),
 'reset_tool_right':cylinder(1,18,12.1,-15.5,20,d=(1,0,0))}
report['access_interference_mm3']={k:max(iv(v,parts[n]) for n in main) for k,v in access.items()}
assert max(report['access_interference_mm3'].values())<.01,report['access_interference_mm3']
hardware=[]
for x,y in POSTS:
    hardware.extend([fuse(cylinder(1.5,28.3,x,y,0),cq.Solid.makeCone(1.5,3,1.7,cq.Vector(x,y,28.3))),
      difference(hexagon(5.5,2.4,x,y,.1),cylinder(1.6,3,x,y,0))])
report['hardware_interference_max_mm3']=max(iv(h,parts[n]) for h in hardware for n in main)
report['hardware_pair_interference_max_mm3']=max(iv(a,b) for i,a in enumerate(hardware) for b in hardware[i+1:])
assert report['hardware_interference_max_mm3']<.01,report['hardware_interference_max_mm3']
assert report['hardware_pair_interference_max_mm3']<.01
report['tool_top_interference_mm3']=max(iv(cylinder(2,20,x,y,30),parts[n]) for x,y in POSTS for n in main)
assert report['tool_top_interference_mm3']<.01

# Positive collisions with fixed retaining surfaces prove stops exist; zero nominal collisions above.
report['capture_stops_mm3']={'rotor_up_0.5':iv(rotor.translate((0,0,.5)),capture),
 'rotor_down_0.5':iv(rotor.translate((0,0,-.5)),base),
 'capture_ring_up_0.1':iv(capture.translate((0,0,.1)),cradle)}
assert min(report['capture_stops_mm3'].values())>.1,report['capture_stops_mm3']
if not args.skip_motion:
    report['rotation_samples']=[]
    for deg in range(0,360,5):
        rr=rotor.rotate((0,0,0),(0,0,1),deg)
        mx=max(iv(rr,parts[n]) for n in main if n!='02_rotor')
        assert mx<.01,(deg,mx)
        report['rotation_samples'].append({'degrees':deg,'max_interference_mm3':mx})
    # Ball seating under spring force, find contact at five points of one detent pitch.
    report['detent_seating']=[]
    for deg in [0,9,18,27,36]:
        rr=rotor.rotate((0,0,0),(0,0,1),deg); lo=28.8; hi=30.2
        for _ in range(12):
            mid=(lo+hi)/2
            if iv(sphere(1.5,mid,0,6.4),rr)>.0001: hi=mid
            else: lo=mid
        spring_length=lo-1.5-22
        assert 3<spring_length<8
        report['detent_seating'].append({'degrees':deg,'ball_center_x':lo,'spring_length':spring_length,
                                         'spring_compression':8-spring_length})

# Official reference is local-only. Shape file includes three assembled bodies and duplicates.
ref=args.reference or pathlib.Path(__file__).parent/'_reference'/'StickS3.stl'
if ref.exists():
    original=tm.load(ref); chunks=original.split(); chosen=[]
    for c in chunks:
        if c.bounds[1,0]<25: chosen.append(c)
    m5=tm.util.concatenate(chosen)
    m5.apply_translation([-12,-24.059725,26.077364])
    report['official_m5_reference']={'source':'https://github.com/m5stack/M5_Hardware/tree/master/Products/K150_StickS3/Structures',
      'assembled_components':len(chosen),'normalized_bounds_mm':m5.bounds.tolist(),'redistributed':False}
    def tmiv(a,b):
        c=tm.boolean.intersection([a,b],engine='manifold');return float(c.volume) if len(c.vertices) else 0.
    report['official_m5_reference']['part_interference_mm3']={n:tmiv(m5,meshes[n]) for n in main}
    assert max(report['official_m5_reference']['part_interference_mm3'].values())<.01
else: m5=mesh(device); report['official_m5_reference']='NOT PROVIDED: envelope-only run'

(OUT/'verification.json').write_text(json.dumps(report,indent=2),encoding='utf-8')
cq.exporters.export(cq.Compound.makeCompound([parts[n] for n in main]),str(OUT/'assembly.step'))

def render(exploded=False):
    import matplotlib
    matplotlib.use('Agg')
    import matplotlib.pyplot as plt
    from mpl_toolkits.mplot3d.art3d import Poly3DCollection
    fig=plt.figure(figsize=(12,9),facecolor='#f4f2ec'); ax=fig.add_subplot(projection='3d')
    colors=['#334852','#bed749','#839ba2','#e1dfd5','#536870']
    lift=[0,13,26,42,64] if exploded else [0]*5
    for j,n in enumerate(main):
        mm=meshes[n].copy(); mm.apply_translation([0,0,lift[j]])
        ax.add_collection3d(Poly3DCollection(mm.triangles,facecolor=colors[j],edgecolor='none',alpha=1))
    mm=m5.copy();mm.apply_translation([0,0,50 if exploded else 0])
    ax.add_collection3d(Poly3DCollection(mm.triangles,facecolor='#d48639',edgecolor='none',alpha=1))
    for h in hardware:
        mm=mesh(h); mm.apply_translation([44 if exploded else 0,0,0])
        ax.add_collection3d(Poly3DCollection(mm.triangles,facecolor='#20292e',edgecolor='none'))
    # Optional ball and spring path are schematic reference components, kept out of print STLs.
    mm=mesh(sphere(1.5,29,0,6.4));mm.apply_translation([0,0,13 if exploded else 0])
    ax.add_collection3d(Poly3DCollection(mm.triangles,facecolor='#b8b8b8',edgecolor='none'))
    ax.set(xlim=(-42,65 if exploded else 42),ylim=(-42,42),zlim=(0,100 if exploded else 40),xlabel='X / mm',ylabel='Y / mm',zlabel='Z / mm')
    ax.set_box_aspect((107 if exploded else 84,84,100 if exploded else 40));ax.view_init(35,-65)
    ax.set_title('ORBIT-10 | '+('EXPLODED ASSEMBLY' if exploded else 'CAPTIVE ROTARY EDC')+'\n75 mm diameter / 30 mm body | ten optional ball detents',fontsize=14)
    fig.text(.05,.02,'Original analytic CAD. M5 official local-only reference shown orange. Not physically printed.\nExploded parts translate in +Z; hardware +44 X. Assembly order: base > rotor > capture > cradle > M5 > frame.',fontsize=10)
    fig.savefig(OUT/('exploded.png' if exploded else 'assembly.png'),dpi=160);plt.close(fig)
render();render(True)
print(json.dumps({k:v for k,v in report.items() if k!='rotation_samples'},indent=2))
