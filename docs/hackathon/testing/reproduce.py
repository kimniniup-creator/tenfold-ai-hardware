"""Independent artifact audit. Run from repository root; writes only .local and requested JSON."""
import argparse, hashlib, io, json, pathlib, subprocess, sys, zipfile
import cadquery as cq
import trimesh as tm

p=argparse.ArgumentParser()
p.add_argument('--output',default='docs/hackathon/testing/evidence.json')
p.add_argument('--refs',nargs=3,default=['9617a85','5671da9','9591aa5'])
p.add_argument('--only',default='')
a=p.parse_args()
root=pathlib.Path.cwd()
names=['471703-pin-array-sidecar','2710405-press-spin-saddle','2673323-concentric-sphere']
report={}
for ref,name in zip(a.refs,names):
    if a.only and not name.startswith(a.only): continue
    sha=subprocess.check_output(['git','rev-parse',ref],text=True).strip()
    prefix='design/hackathon/'+name
    data=subprocess.check_output(['git','archive','--format=zip',sha,prefix])
    dest=root/'.local'/'audit'/sha
    dest.mkdir(parents=True,exist_ok=True)
    zipfile.ZipFile(io.BytesIO(data)).extractall(dest)
    folder=dest/prefix
    row={'sha':sha,'artifacts':{}}
    def scan():
        result={}
        for f in sorted([*folder.glob('*'),*(folder/'exports').glob('*')]):
            if f.suffix=='.stl':
                m=tm.load_mesh(f)
                result[f.name]={'sha256':hashlib.sha256(f.read_bytes()).hexdigest(),'watertight':bool(m.is_watertight),'winding':bool(m.is_winding_consistent),'components':len(m.split(only_watertight=False)),'volume_mm3':round(float(m.volume),4),'bounds_mm':m.bounds.round(4).tolist()}
            elif f.suffix=='.step':
                solids=cq.importers.importStep(str(f)).solids().vals()
                result[f.name]={'solids':len(solids),'valid':all(s.isValid() for s in solids),'volume_mm3':round(sum(s.Volume() for s in solids),4)}
        return result
    row['artifacts']=scan()
    run=subprocess.run([sys.executable,str(folder/'build.py')],capture_output=True,text=True)
    row['regeneration_exit']=run.returncode
    (dest/'build.log').write_text(run.stdout+'\n'+run.stderr,encoding='utf8')
    row['regenerated']=scan()
    row['geometry_metrics_reproduced']=run.returncode==0 and all({k:v for k,v in value.items() if k!='sha256'}=={k:v for k,v in row['regenerated'][file].items() if k!='sha256'} for file,value in row['artifacts'].items())
    report[name]=row
    print(name,sha,run.returncode,row['geometry_metrics_reproduced'],flush=True)
pathlib.Path(a.output).write_text(json.dumps(report,indent=2),encoding='utf8')
