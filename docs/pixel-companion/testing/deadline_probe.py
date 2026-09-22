"""Actual loopback slow HTTP stream; HTTPS transport is adapted only at urlopen test boundary."""
import argparse,importlib.util,json,os,time,threading,hashlib,sys
from pathlib import Path
from http.server import BaseHTTPRequestHandler,ThreadingHTTPServer
from unittest.mock import patch
import urllib.request
p=argparse.ArgumentParser();p.add_argument('--source',type=Path,required=True);p.add_argument('--out',type=Path,required=True);a=p.parse_args()
spec=importlib.util.spec_from_file_location('candidate',a.source);m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m)
body=json.dumps({'choices':[{'message':{'content':json.dumps({'action':'happy','text':'我在。'})}}]}).encode()
class Handler(BaseHTTPRequestHandler):
 def log_message(self,*_):pass
 def do_POST(self):
  self.rfile.read(int(self.headers.get('Content-Length',0)))
  self.send_response(200);self.send_header('Content-Length',str(len(body)));self.end_headers()
  try:
   if self.path=='/fast':self.wfile.write(body);self.wfile.flush()
   else:
    for b in body:
     self.wfile.write(bytes([b]));self.wfile.flush();time.sleep(0.5)
  except (BrokenPipeError,ConnectionResetError,ConnectionAbortedError):pass
server=ThreadingHTTPServer(('127.0.0.1',0),Handler);threading.Thread(target=server.serve_forever,daemon=True).start();original=urllib.request.build_opener(urllib.request.ProxyHandler({})).open
results=[]
try:
 for path in ['/fast','/slow']:
  def adapted(req,timeout):
   # Synthetic body only; no credential forwarded to loopback fixture.
   r=urllib.request.Request('http://127.0.0.1:'+str(server.server_port)+path,data=req.data,headers={'Content-Type':'application/json'})
   return original(r,timeout=timeout)
  env={'PET_API_URL':'https://synthetic.invalid'+path,'PET_API_KEY':'SYNTHETIC_NOT_A_KEY','PET_MODEL':'test'}
  errors=[]
  def trace(frame,event,arg):
   if event=="exception" and Path(frame.f_code.co_filename).resolve()==a.source.resolve():errors.append(type(arg[1]).__name__+": "+str(arg[1]))
   return trace
  start=time.monotonic();sys.settrace(trace)
  with patch.dict(os.environ,env,clear=True),patch.object(m.urllib.request,'urlopen',side_effect=adapted):reply=getattr(m,'_request',m.respond)({'presses':3,'duration_ms':10000,'held_ms':100,'mean_interval_ms':200})
  sys.settrace(None);elapsed=time.monotonic()-start
  ok=reply['source']=='agent' if path=='/fast' else reply['source']=='local' and 7.5<=elapsed<=10.5
  results.append({'path':path,'elapsed_seconds':round(elapsed,3),'source':reply['source'],'errors':errors,'status':'PASS' if ok else 'FAIL'})
finally:server.shutdown();server.server_close()
out={'source_sha256':hashlib.sha256(a.source.read_bytes()).hexdigest(),'layer':'actual loopback HTTP read1/socket; HTTPS adapted at transport boundary; no live provider','results':results};a.out.write_text(json.dumps(out,indent=2)+'\n');print(json.dumps(out,indent=2))
