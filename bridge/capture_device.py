"""Read-only status capture; never injects buttons or writes flash."""
import argparse
import json
import time
from pathlib import Path
import serial

def main():
    parser=argparse.ArgumentParser()
    parser.add_argument("--port",required=True)
    parser.add_argument("--seconds",type=int,default=90)
    parser.add_argument("--out",default=".delivery/pixel-physical.ndjson")
    args=parser.parse_args()
    output=Path(args.out);output.parent.mkdir(parents=True,exist_ok=True)
    port=serial.Serial()
    port.port=args.port;port.baudrate=115200;port.timeout=.1;port.write_timeout=.2
    port.dtr=False;port.rts=False
    port.open()
    with output.open("x",encoding="utf-8") as log, port:
        deadline=time.monotonic()+min(max(args.seconds,1),600)
        next_query=0
        while time.monotonic()<deadline:
            if time.monotonic()>=next_query:
                port.write(b'{"type":"hello_request"}\n');next_query=time.monotonic()+1
            line=port.read_until(b'\n',1024)
            if not line:continue
            try:item=json.loads(line)
            except (ValueError,UnicodeError):continue
            record={"host_monotonic":round(time.monotonic(),3),"device":item}
            wire=json.dumps(record,ensure_ascii=False)
            print(wire,flush=True);log.write(wire+"\n");log.flush()

if __name__=="__main__":main()
