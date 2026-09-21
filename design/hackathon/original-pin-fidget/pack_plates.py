"""Arrange already oriented STL parts into three <=180mm trial plates."""
from pathlib import Path
import json,hashlib
import trimesh
import numpy as np
R=Path(__file__).resolve().parent;E=R/'exports';O=R/'print_plates';O.mkdir(exist_ok=True)
plates={
'01_calibration': [('calibration_guide',0,0),('calibration_chamber',0,24),('calibration_roof',22,24)]+[('06_pin',44+12*i,24) for i in range(3)],
'02_structure': [('01_guide_plate',0,0),('02_pin_spacer',76,0),('03_structural_frame',0,48)],
'03_details': [('04_m5_sled',0,0),('05_retaining_rail',0,44),('05_retaining_rail',0,61)]+[('06_pin',76+12*x,12*y) for y in range(3) for x in range(4)]}
report={}
for name,items in plates.items():
    meshes=[];bounds=[];records=[]
    for part,x,y in items:
        src=E/(part+'.stl');m=trimesh.load_mesh(src);m.apply_translation([x,y,0]);meshes.append(m);bounds.append(m.bounds)
        records.append({'file':part+'.stl','translation_mm':[x,y,0],'source_sha256':hashlib.sha256(src.read_bytes()).hexdigest()})
    for i,b in enumerate(bounds):
        for c in bounds[i+1:]:assert np.any(b[1,:2]<=c[0,:2]) or np.any(c[1,:2]<=b[0,:2]),(name,i)
    m=trimesh.util.concatenate(meshes);assert m.is_watertight and len(m.split())==len(items)
    assert m.extents[0]<=180 and m.extents[1]<=180 and abs(m.bounds[0,2])<1e-5
    m.export(O/(name+'.stl'))
    report[name]={'instances':len(items),'bounds_mm':m.extents.round(3).tolist(),'watertight':True,'disjoint_xy_aabb':True,'infill_percent':25 if name=='02_structure' else 100,'items':records}
(O/'manifest.json').write_text(json.dumps(report,indent=2),encoding='utf-8')
print(json.dumps({n:{k:v for k,v in r.items() if k!='items'} for n,r in report.items()},indent=2))
