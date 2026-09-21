"""Independently intersect actual official shell components with pin assembly STEP."""
import argparse,pathlib,json,subprocess,hashlib
import cadquery as cq
import trimesh as tm
import numpy as np
p=argparse.ArgumentParser();p.add_argument('--sha',required=True);p.add_argument('--reference',required=True);p.add_argument('--output',required=True);a=p.parse_args()
sha=subprocess.check_output(['git','rev-parse',a.sha],text=True).strip();root=pathlib.Path('.local/original-audit')/sha/'design/hackathon/original-pin-fidget/exports'
ref=pathlib.Path(a.reference);chunks=tm.load_mesh(ref).split(only_watertight=False);device=tm.util.concatenate([chunks[i] for i in [0,3,4]])
device.apply_translation([-12,-24.059725,14.077364]);device.apply_transform(tm.transformations.rotation_matrix(-np.pi/2,[0,0,1]));device.apply_translation([35,21,11.7])
shapes=cq.importers.importStep(str(root/'assembly_hardware.step')).solids().vals();values=[]
for s in shapes:
    v,f=s.tessellate(.035,.12);m=tm.Trimesh([p.toTuple() for p in v],f,process=True);m.fix_normals()
    result=tm.boolean.intersection([device,m],engine='manifold');values.append(float(result.volume) if len(result.faces) else 0.)
out={'sha':sha,'reference_sha256':hashlib.sha256(ref.read_bytes()).hexdigest(),'transform':'components0/3/4; translate(-12,-24.059725,14.077364); Rz(-90deg); translate(35,21,11.7)','device_bounds_mm':device.bounds.tolist(),'assembly_solids':len(shapes),'intersection_mm3_by_solid':values,'max_intersection_mm3':max(values),'physical_operation_tested':False}
pathlib.Path(a.output).write_text(json.dumps(out,indent=2),encoding='utf8');print(out['max_intersection_mm3'])
