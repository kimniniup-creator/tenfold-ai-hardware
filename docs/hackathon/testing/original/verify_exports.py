"""Compare tester-regenerated STL geometry with committed STL and import STEP solids."""
import argparse,pathlib,subprocess,io,json
import cadquery as cq
import trimesh as tm
import numpy as np
p=argparse.ArgumentParser();p.add_argument('--sha',required=True);p.add_argument('--path',required=True);p.add_argument('--output',required=True);a=p.parse_args()
sha=subprocess.check_output(['git','rev-parse',a.sha],text=True).strip();folder=pathlib.Path('.local/original-audit')/sha/a.path
files=subprocess.check_output(['git','ls-tree','-r','--name-only',sha,a.path],text=True).splitlines();out={'sha':sha,'path':a.path,'stl':{},'step':{}}
for file in files:
    relative=pathlib.PurePosixPath(file).relative_to(a.path);f=folder/relative
    if f.suffix=='.stl':
        committed=tm.load_mesh(io.BytesIO(subprocess.check_output(['git','show',sha+':'+file])),file_type='stl');m=tm.load_mesh(f)
        out['stl'][str(relative)]={'committed_volume_mm3':float(committed.volume),'regenerated_volume_mm3':float(m.volume),'volume_equal_1e_4':bool(abs(committed.volume-m.volume)<1e-4),'bounds_equal_1e_4':bool(np.allclose(committed.bounds,m.bounds,atol=1e-4)),'watertight':bool(m.is_watertight),'components':len(m.split(only_watertight=False))}
    if f.suffix=='.step':
        s=cq.importers.importStep(str(f)).solids().vals();out['step'][str(relative)]={'solids':len(s),'valid':all(t.isValid() for t in s),'positive_volume':all(t.Volume()>0 for t in s)}
out['all_stl_match']=all(x['volume_equal_1e_4'] and x['bounds_equal_1e_4'] for x in out['stl'].values());pathlib.Path(a.output).write_text(json.dumps(out,indent=2),encoding='utf8');print(sha,len(out['stl']),len(out['step']),out['all_stl_match'])
