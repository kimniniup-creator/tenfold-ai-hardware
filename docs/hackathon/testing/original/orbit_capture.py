"""Sample rigid offsets/tilts of the captured orbit; not a continuous escape-path proof."""
import argparse,json,pathlib,subprocess,io,zipfile
import cadquery as cq
p=argparse.ArgumentParser();p.add_argument('--sha',required=True);p.add_argument('--output',required=True);a=p.parse_args()
sha=subprocess.check_output(['git','rev-parse',a.sha],text=True).strip();path='design/hackathon/original-orbit-fidget';d=pathlib.Path('.local/original-audit')/sha
zipfile.ZipFile(io.BytesIO(subprocess.check_output(['git','archive','--format=zip',sha,path]))).extractall(d)
def load(n):return cq.importers.importStep(str(d/path/(n+'.step'))).val()
r=load('02_rotor');fixed={n:load(n) for n in ['01_base','03_capture_ring','04_m5_cradle','05_face_frame']}
def collisions(s):return {n:round(sum(v.Volume() for v in s.intersect(f).Solids()),6) for n,f in fixed.items()}
report={'sha':sha,'physical_tested':False,'scope':'Sampled rigid translations/tilts only; does not certify all escape paths or elastic deformation. Positive intersection identifies a blocked pose.','nominal':collisions(r),'tilts':[],'translations':[]}
for axis in [(1,0,0),(0,1,0),(1,1,0)]:
 for angle in [.25,.5,1,2,5]:
  result=collisions(r.rotate((0,0,6.4),(axis[0],axis[1],6.4),angle))
  report['tilts'].append({'axis_xy':list(axis[:2]),'degrees':angle,'intersection_mm3':result})
for v in [(0,0,.5),(0,0,-.5),(.5,0,0),(1,0,0),(0,1,0),(2,0,0)]:report['translations'].append({'offset_mm':v,'intersection_mm3':collisions(r.translate(v))})
pathlib.Path(a.output).write_text(json.dumps(report,indent=2)+'\n',encoding='utf-8');print(json.dumps(report))
