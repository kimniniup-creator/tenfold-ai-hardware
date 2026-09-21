"""Independent exhaustive press-saddle hardware collision probe on frozen source."""
import importlib.util, itertools, json, pathlib
f=next(pathlib.Path('.local/audit').glob('5671*/design/hackathon/*/build.py'))
s=importlib.util.spec_from_file_location('frozen',f); m=importlib.util.module_from_spec(s); s.loader.exec_module(m)
out={'sha':'5671da9560c9cf4d59e8d8b7a0ae00e196fc6e8b','cases':{}}
for width in [10,22,30]:
    m.P['static_grip_width']=width
    parts=m.build(); hw=m.hardware(); hits=[]
    for hn,h in hw.items():
        for pn,p in parts.items():
            v=sum(s.Volume() for s in h.intersect(p).solids().vals())
            if v>1e-5:hits.append([hn,pn,round(v,6)])
    for (n,h),(n2,h2) in itertools.combinations(hw.items(),2):
        v=sum(s.Volume() for s in h.intersect(h2).solids().vals())
        if v>1e-5:hits.append([n,n2,round(v,6)])
    out['cases'][str(width)]=hits
pathlib.Path('docs/hackathon/testing/hardware_probe.json').write_text(json.dumps(out,indent=2),encoding='utf8')
print(json.dumps(out))
