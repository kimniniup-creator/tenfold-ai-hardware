"""Re-run fixed sphere generator at endpoints in the tester snapshot."""
import pathlib,subprocess,sys,json,trimesh as tm
f=next(pathlib.Path('.local/audit').glob('8ba49*/design/hackathon/*/build.py'))
result={'sha':'8ba49f0d8c56d5c531611860dcf0996722f94a82','scheme':'2673323-concentric-sphere','cases':{}}
for diameter in [50,80]:
    dest=f.parent/f'_independent_d{diameter}'
    run=subprocess.run([sys.executable,str(f),'--ball-diameter',str(diameter),'--output',str(dest)],capture_output=True,text=True)
    row={'exit':run.returncode}
    if run.returncode==0:
        row['meshes']={p.name:{'watertight':bool((m:=tm.load_mesh(p)).is_watertight),'components':len(m.split(only_watertight=False)),'volume_mm3':float(m.volume)} for p in dest.glob('*.stl')}
        generated=json.loads((dest/'verification.json').read_text())
        row['reexecuted_hardware_overlap_mm3']=generated['hardware_interference_max_mm3']
        row['reexecuted_tool_overlap_mm3']=generated['tool_interference_max_mm3']
    result['cases'][str(diameter)]=row
    print(diameter,row,flush=True)
pathlib.Path('docs/hackathon/testing/ball-range-retest.json').write_text(json.dumps(result,indent=2),encoding='utf8')
