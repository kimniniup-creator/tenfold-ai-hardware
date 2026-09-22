"""Read-only import of a fixed Git bridge snapshot; no serial or network access."""
import argparse
import importlib.util
import json
from pathlib import Path
import subprocess
from unittest.mock import patch

parser=argparse.ArgumentParser()
parser.add_argument('--repo',required=True)
parser.add_argument('--revision',required=True)
args=parser.parse_args()
sha=subprocess.check_output(['git','-C',args.repo,'rev-parse',args.revision],text=True).strip()
source=subprocess.check_output(['git','-C',args.repo,'show',sha+':bridge/companion.py'])
runtime=Path(__file__).parent/'runtime'
runtime.mkdir(exist_ok=True)
module_path=runtime/'companion.py'
module_path.write_bytes(source)
spec=importlib.util.spec_from_file_location('companion_under_test',module_path)
module=importlib.util.module_from_spec(spec)
spec.loader.exec_module(module)
results=[]
def case(name,check):
    try:
        ok=bool(check())
        results.append({'case':name,'pass':ok})
    except Exception as exc:
        results.append({'case':name,'pass':False,'exception':type(exc).__name__})

def hello(**extra):
    return dict(type='hello',protocol=2,session='s1',epoch=0,quiet=False,**extra)
def rhythm(window=1,epoch=0):
    return dict(type='rhythm',protocol=2,session='s1',epoch=epoch,window=window,
                presses=3,duration_ms=10000,held_ms=300,mean_interval_ms=400,quiet=False,candidate=True)
def invalid_epoch():
    gate=module.Gate();item=hello();item['epoch']={};gate.accept(item,0)
    return not gate.accept(rhythm(),1)
def cooldown():
    gate=module.Gate();gate.accept(hello(),0)
    return gate.accept(rhythm(),0) and not gate.accept(rhythm(2),59) and gate.accept(rhythm(3),60)
def duplicate():
    gate=module.Gate();gate.accept(hello(),0);gate.accept(rhythm(),0)
    return not gate.accept(rhythm(),61)
def quiet_old():
    gate=module.Gate();gate.accept(hello(),0);item=hello();item.update(epoch=1,quiet=True);gate.accept(item,1)
    return not gate.accept(rhythm(2,0),61) and gate.quiet
def rejected(text):
    try: module.validate_reply({'action':'happy','text':text})
    except (ValueError,TypeError): return True
    return False
def fallback_no_key():
    with patch.dict(module.os.environ,{},clear=True):
        return module.respond({})['source']=='local'
def fallback_timeout():
    with patch.dict(module.os.environ,{'PET_API_URL':'https://example.invalid','PET_API_KEY':'synthetic','PET_MODEL':'test'},clear=True),patch.object(module.urllib.request,'urlopen',side_effect=TimeoutError):
        return module.respond({})['source']=='local'

case('malformed_hello_epoch_never_crashes',invalid_epoch)
case('cooldown_60_seconds',cooldown)
case('duplicate_window_rejected',duplicate)
case('quiet_rejects_old_epoch',quiet_old)
case('punitive_phrase_rejected',lambda:rejected('你太懒了，快来陪我。'))
case('emotional_inference_rejected',lambda:rejected('你现在很难过。'))
case('no_key_honest_local',fallback_no_key)
case('timeout_honest_local',fallback_timeout)
print(json.dumps({'revision':sha,'scope':'host import, synthetic frames and mocked failures; no serial/network','results':results},ensure_ascii=False,indent=2))
