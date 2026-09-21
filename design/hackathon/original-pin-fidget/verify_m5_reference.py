"""Verify local official M5 mesh fits a conservative guard envelope; never redistribute it.
Use --reference to point to official StickS3.stl downloaded by the user.
Default assembly only. Proven containment + empty guard intersections implies no source mesh overlap.
"""
import argparse,hashlib,json
from pathlib import Path
import numpy as np
import trimesh
import cadquery as cq
p=argparse.ArgumentParser();p.add_argument('--reference',required=True);a=p.parse_args()
R=Path(__file__).resolve().parent; O=R/'exports'
raw=Path(a.reference).read_bytes();m=trimesh.load_mesh(a.reference)
cs=m.split(only_watertight=False); chosen=[c for c in cs if c.bounds[1,0]<25]
assert len(chosen)==3,(len(cs),len(chosen))
# Right-handed rigid rotation: original +Y -> case +X, original +X -> case -Y.
T=np.array([[0,1,0,11-.058790501207113266],[-1,0,0,33],[0,0,1,11.7+14.077363967895508],[0,0,0,1.]])
source=[]
for c in chosen:c.apply_transform(T);source.append(c)
v=np.vstack([c.vertices for c in source]);lo=v.min(0);hi=v.max(0)
guard_lo=np.array([10.99,8.99,11.69]);guard_hi=np.array([59.01,33.01,26.71])
assert np.all(lo>=guard_lo) and np.all(hi<=guard_hi),(lo,hi)
g=cq.Workplane('XY').box(*(guard_hi-guard_lo),centered=False).translate(tuple(guard_lo))
asmb=cq.importers.importStep(str(O/'assembly_hardware.step'))
volumes=[]
for s in asmb.solids().vals():
 q=s.intersect(g.val());volumes.append(float(q.Volume()))
assert all(abs(z)<1e-5 for z in volumes),volumes
report={'source_sha256':hashlib.sha256(raw).hexdigest(),'source_url':'https://github.com/m5stack/M5_Hardware/tree/master/Products/K150_StickS3/Structures',
 'source_connected_shells':len(cs),'assembled_shells_used':3,'selection':'source Xmax<25; excludes displaced duplicates',
 'right_handed_transform':T.tolist(),'transformed_bounds':[lo.tolist(),hi.tolist()],'guard_bounds':[guard_lo.tolist(),guard_hi.tolist()],
 'guard_margin_nominal_mm':.01,'hardware_assembly_solids':len(volumes),'guard_intersection_volumes_mm3':volumes,
 'method':'All official assembled vertices inside axis-aligned convex guard, hence all triangles inside guard. Guard CSG intersections empty against every printed/hardware solid. Conservative containment proof, not direct mesh boolean.',
 'not_validated':'button actuation, cable electrical connection, thermal/RF, physical print or friction'}
(O/'m5_reference_validation.json').write_text(json.dumps(report,indent=2),encoding='utf-8');print(json.dumps(report,indent=2))
