"""Exercise real respond parent deadline with an actual deliberately stalled Python child."""
import argparse,hashlib,importlib.util,json,os,subprocess,sys,time
from pathlib import Path
from unittest.mock import patch
p=argparse.ArgumentParser();p.add_argument('--source',type=Path,required=True);p.add_argument('--out',type=Path,required=True);a=p.parse_args()
spec=importlib.util.spec_from_file_location('candidate',a.source);m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m)
original_run=subprocess.run;original_popen=subprocess.Popen;children=[];timeouts=[]
def popen(*args,**kwargs):
 child=original_popen(*args,**kwargs);children.append(child);return child
def stalled_run(args,**kwargs):
 timeouts.append(kwargs.get('timeout'))
 return original_run([sys.executable,'-c','import time; time.sleep(30)'],**kwargs)
env={'PET_API_URL':'https://synthetic.invalid','PET_API_KEY':'SYNTHETIC_NOT_A_KEY','PET_MODEL':'test'}
started=time.monotonic()
with patch.dict(os.environ,env,clear=True),patch.object(m.subprocess,'run',side_effect=stalled_run),patch.object(subprocess,'Popen',side_effect=popen):result=m.respond({'presses':3})
elapsed=time.monotonic()-started
reaped=bool(children) and all(c.returncode is not None and c.poll() is not None for c in children)
out={'source_sha256':hashlib.sha256(a.source.read_bytes()).hexdigest(),'layer':'actual respond parent + real OS stalled child, child request implementation substituted; no live network','elapsed_seconds':round(elapsed,3),'configured_timeout':timeouts,'children':len(children),'all_children_killed_and_reaped':reaped,'source':result.get('source'),'status':'PASS' if 7.5<=elapsed<=10.5 and reaped and result.get('source')=='local' and timeouts==[8] else 'FAIL'}
a.out.write_text(json.dumps(out,indent=2)+'\n');print(json.dumps(out,indent=2))
