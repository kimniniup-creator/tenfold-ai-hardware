"""Independent tests of an exact bridge source; synthetic HTTP/serial boundaries, no COM access."""
import argparse, contextlib, hashlib, importlib.util, io, json, os, sys, types, runpy
from pathlib import Path
from unittest.mock import patch

p = argparse.ArgumentParser(); p.add_argument('--source', type=Path, required=True); p.add_argument('--out', type=Path, required=True)
a = p.parse_args()
spec = importlib.util.spec_from_file_location('candidate', a.source); m = importlib.util.module_from_spec(spec); spec.loader.exec_module(m)
results = []
def test(name, fn):
    try: fn(); results.append({'id':name,'status':'PASS'})
    except Exception as e: results.append({'id':name,'status':'FAIL','error':type(e).__name__+': '+str(e)})
def check(v):
    if not v: raise AssertionError('expectation false')
def hello(**kw): return dict(type='hello',protocol=2,session='test-session',epoch=0,quiet=False,**kw)
def rhythm(**kw):
    d=dict(type='rhythm',protocol=2,session='test-session',epoch=0,window=1,presses=3,duration_ms=10000,held_ms=300,mean_interval_ms=200,quiet=False,candidate=True); d.update(kw); return d
def gate():
    g=m.Gate();g.accept(hello(),0);return g

def cooldown():
    g=gate();check(g.accept(rhythm(),0));check(not g.accept(rhythm(window=2),59.999));check(g.accept(rhythm(window=3),60))
def duplicate():
    g=gate();check(g.accept(rhythm(),0));check(not g.accept(rhythm(),100));check(not g.accept(rhythm(window=0),200))
def quiet():
    g=gate();h=hello();h.update(epoch=1,quiet=True);g.accept(h,1);check(not g.accept(rhythm(epoch=1,quiet=True),100));check(not g.accept(rhythm(epoch=0,window=2),200))
def new_session():
    g=gate();check(g.accept(rhythm(),0));h=hello();h['session']='new';g.accept(h,1);check(not g.accept(rhythm(window=2),100));check(not g.accept(rhythm(session='new'),30));check(g.accept(rhythm(session='new',window=2),60))
def numeric():
    for k in ['epoch','window','presses','duration_ms','held_ms','mean_interval_ms']:
        for v in [True,'3',None,-1]: check(not gate().accept(rhythm(**{k:v}),100))
def bad_hello():
    for value in ['bad',None,{},True,-1]:
        g=gate();h=hello();h['epoch']=value;g.accept(h,0);check(g.accept(rhythm(),100))
def reply_reject():
    for v in [{}, {'action':'exec','text':'hello'}, {'action':'happy','text':'a'*73}, {'action':'happy','text':'x\ny'}, {'action':'happy','text':'检测到焦虑'}, {'action':'happy','text':'hello','code':'x'}]:
        try: m.validate_reply(v)
        except (ValueError,TypeError): continue
        raise AssertionError('bad reply accepted')
def no_credentials():
    with patch.dict(os.environ,{},clear=True),patch.object(m.urllib.request,'urlopen',side_effect=AssertionError('network forbidden')):check(m.respond({})['source']=='local')
class Response:
    def __init__(self,data):
        self.data=data;self.offset=0;self.fp=types.SimpleNamespace(raw=types.SimpleNamespace(_sock=types.SimpleNamespace(settimeout=lambda _:None)))
    def __enter__(self):return self
    def __exit__(self,*_):pass
    def isclosed(self):return self.offset>=len(self.data)
    def read(self,n):return self.data[:n]
    def read1(self,n):
        chunk=self.data[self.offset:self.offset+n];self.offset+=len(chunk);return chunk
def request_case(data=None,error=None):
    env={'PET_API_URL':'https://example.invalid/v1/chat/completions','PET_API_KEY':'SYNTHETIC_NOT_A_KEY','PET_MODEL':'test'}
    calls=[]
    def open_(request,timeout):
        calls.append((request,timeout))
        if error:raise error
        return Response(data)
    with patch.dict(os.environ,env,clear=True),patch.object(m.urllib.request,'urlopen',side_effect=open_): out=getattr(m,'_request',m.respond)({'presses':3,'duration_ms':10000,'held_ms':100,'mean_interval_ms':200})
    check(calls[0][1]==8);return out

def serial_case(chunks, fail_disconnect=False):
    writes=[];opens=[]
    class End(Exception):pass
    class Port:
        def __enter__(self):return self
        def __exit__(self,*_):pass
        def write(self,b):writes.append(b)
        def read(self,n):
            if chunks:return chunks.pop(0)
            if fail_disconnect and len(opens)==1:raise OSError('synthetic disconnect')
            raise End()
    def open_(*args,**kwargs):opens.append(args);return Port()
    serial=types.SimpleNamespace(Serial=open_,SerialException=OSError)
    with patch.dict(sys.modules,{'serial':serial}),patch.object(sys,'argv',['bridge','--port','SYNTHETIC']),patch.dict(os.environ,{},clear=True),contextlib.redirect_stdout(io.StringIO()):
        try:
            if fail_disconnect:runpy.run_path(str(a.source),run_name="__main__")
            else:m.main()
        except End:pass
    return writes,opens

def stale_quiet():
    h=hello();h.update(epoch=1,quiet=True)
    writes,_=serial_case([b''.join((json.dumps(x)+'\n').encode() for x in [hello(),rhythm(),h])]);check(not any(b'"type": "reply"' in x for x in writes))
def reconnect():
    _,opens=serial_case([],True);check(len(opens)>=2)


def reconnect_cooldown():
    calls=[];opens=[]
    class End(Exception):pass
    class Port:
        def __init__(self,index):self.index=index;self.reads=0
        def __enter__(self):return self
        def __exit__(self,*_):pass
        def write(self,b):pass
        def read(self,n):
            self.reads+=1
            if self.reads==1:return b''.join((json.dumps(x)+'\n').encode() for x in [hello(),rhythm(window=self.index)])
            if self.index==1:raise OSError('synthetic reconnect')
            raise End()
    def open_(*args,**kwargs):opens.append(args);return Port(len(opens))
    def respond(summary):calls.append(summary);return dict(m.FALLBACK)
    serial=types.SimpleNamespace(Serial=open_,SerialException=OSError)
    with patch.dict(sys.modules,{'serial':serial}),patch.object(sys,'argv',['bridge','--port','SYNTHETIC']),patch.object(m,'respond',side_effect=respond),contextlib.redirect_stdout(io.StringIO()):
        try:m.main()
        except End:pass
    check(len(opens)==2 and len(calls)==1)
def phrases():
    for text in ['我在。','我在，陪你待会儿。','嗯，接住了。','慢慢来就好。','安静待着，也很好。']:check(m.validate_reply({'action':'rest','text':text})['source']=='agent')
    try:m.validate_reply({'action':'happy','text':'A new unapproved phrase'})
    except ValueError:return
    raise AssertionError('unapproved phrase accepted')
def threshold():
    g=gate();check(not g.accept(rhythm(presses=0),0));check(not g.accept(rhythm(presses=2,window=2),1));check(g.accept(rhythm(presses=3,window=3),2))

test('G01_cooldown_60s_boundary',cooldown)
test('G02_duplicate_and_out_of_order',duplicate)
test('G03_quiet_and_old_epoch',quiet)
test('G04_new_session_retains_cooldown',new_session)
test('G05_numeric_schema',numeric)
test('G06_malformed_hello_no_crash',bad_hello)
test('V01_valid_reply',lambda:check(m.validate_reply({'action':'blink','text':'我在。'})['source']=='agent'))
test('V02_reject_bad_reply',reply_reject)
test('R01_no_credentials_local_no_network',no_credentials)
test('R02_timeout_fallback',lambda:check(request_case(error=TimeoutError())['source']=='local'))
test('R03_http_failure_fallback',lambda:check(request_case(error=OSError('synthetic500'))['source']=='local'))
test('R04_malformed_json_fallback',lambda:check(request_case(b'bad json')['source']=='local'))
test('R05_oversized_response_fallback',lambda:check(request_case(b'x'*16385)['source']=='local'))
test('R06_valid_synthetic_provider',lambda:check(request_case(json.dumps({'choices':[{'message':{'content':json.dumps({'action':'happy','text':'我在。'})}}]}).encode())['source']=='agent'))
test('M01_late_reply_quiet_suppressed',stale_quiet)
test('M02_serial_disconnect_reconnect',reconnect)
test('G07_three_press_threshold',threshold)
if hasattr(m,'run_once'):
    test('M03_reconnect_preserves_actual_gate_cooldown',reconnect_cooldown)
    test('V03_exact_five_phrases',phrases)
out={'source_sha256':hashlib.sha256(a.source.read_bytes()).hexdigest(),'layer':'HOST actual candidate imported; synthetic HTTP and serial boundaries; no live model or device','results':results}
a.out.parent.mkdir(parents=True,exist_ok=True);a.out.write_text(json.dumps(out,ensure_ascii=False,indent=2)+'\n',encoding='utf-8');print(json.dumps(out,ensure_ascii=False,indent=2))
