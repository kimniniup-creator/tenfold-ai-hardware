"""Small explicit ADB UI helper. Captures test-device screens/XML, never touches a phone by default."""
import argparse,json,pathlib,re,shlex,subprocess,xml.etree.ElementTree as ET
p=argparse.ArgumentParser();p.add_argument('--serial',default='emulator-5554');p.add_argument('--adb',default='E:/Android/Sdk/platform-tools/adb.exe')
p.add_argument('--out',default='.local/android-ui');p.add_argument('action',choices=['snapshot','tap','fill']);p.add_argument('value');p.add_argument('--index',type=int,default=0);p.add_argument('--replace',action='store_true')
a=p.parse_args();out=pathlib.Path(a.out);out.mkdir(parents=True,exist_ok=True)
def adb(*args):return subprocess.check_output([a.adb,'-s',a.serial,*args],timeout=45)
def layout():
 adb('shell','uiautomator','dump','/sdcard/tenfold-test-window.xml')
 return adb('shell','cat','/sdcard/tenfold-test-window.xml')
def tap(n):
 x1,y1,x2,y2=map(int,re.findall(r'\d+',n.attrib['bounds']));adb('shell','input','tap',str((x1+x2)//2),str((y1+y2)//2))
if a.action=='snapshot':
 raw=layout();(out/(a.value+'.xml')).write_bytes(raw)
 (out/(a.value+'.png')).write_bytes(adb('exec-out','screencap','-p'))
 root=ET.fromstring(raw);print(json.dumps([{k:n.get(k) for k in ['text','class','bounds']} for n in root.iter('node') if n.get('text') or n.get('class')=='android.widget.EditText'],ensure_ascii=False))
else:
 root=ET.fromstring(layout())
 if a.action=='tap':
  ns=[n for n in root.iter('node') if n.get('text')==a.value or n.get('content-desc')==a.value]
  if not ns:raise SystemExit('Exact label absent; inspect a fresh snapshot')
  tap(ns[a.index])
 else:
  ns=[n for n in root.iter('node') if n.get('class')=='android.widget.EditText']
  tap(ns[a.index]);adb('shell','input','keyevent','123')
  if a.replace:adb('shell','input','keycombination','113','29');adb('shell','input','keyevent','67')
  adb('shell','input','text',shlex.quote(a.value.replace(' ','%s')))
