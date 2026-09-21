"""Check the press candidate against local-only official assembled M5 shell meshes."""
import argparse,hashlib,importlib.util,json,pathlib,sys
import numpy as np,trimesh as tm
p=argparse.ArgumentParser();p.add_argument('--sha',required=True);p.add_argument('--reference',required=True);p.add_argument('--output',required=True);a=p.parse_args()
folder=pathlib.Path('.local/original-audit')/a.sha/'design/hackathon/original-press-spin'
spec=importlib.util.spec_from_file_location('press_cad',folder/'cad.py');cad=importlib.util.module_from_spec(spec);spec.loader.exec_module(cad)
allref=tm.load_mesh(a.reference).split(only_watertight=False);reference=[]
T=np.array([[0,1,0,-24.059725],[1,0,0,-12],[0,0,-1,5.722636],[0,0,0,1.]])
for i in [0,3,4]:
 m=allref[i].copy();m.apply_transform(T);reference.append(m)
def mesh(s):
 v,f=s.val().tessellate(.035,.12);return tm.Trimesh(np.array([x.toTuple() for x in v]),np.array(f),process=True)
r={'sha':a.sha,'reference_sha256':hashlib.sha256(pathlib.Path(a.reference).read_bytes()).hexdigest(),'reference_components':[0,3,4],'raw_to_assembly':T.tolist(),'bounds_mm':tm.util.concatenate(reference).bounds.tolist(),'physical_tested':False,'intersection_mm3':{}}
parts=cad.parts();parts.update({k:v for k,v in cad.alternatives().items() if k.startswith('metal')});parts.update({'hardware_'+k:v for k,v in cad.metal_reference().items()})
for n,s in parts.items():
 m=mesh(s);vol=sum(max(0,tm.boolean.intersection([m,v],engine='manifold').volume) for v in reference);r['intersection_mm3'][n]=float(vol)
r['max_intersection_mm3']=max(r['intersection_mm3'].values());pathlib.Path(a.output).write_text(json.dumps(r,indent=2)+'\n',encoding='utf-8');print(r['max_intersection_mm3'])
