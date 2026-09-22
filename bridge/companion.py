"""Optional USB companion bridge. Secrets stay in environment variables."""
import argparse
import concurrent.futures
import json
import os
import subprocess
import sys
import time
import urllib.request
from serial_frames import open_device

ACTIONS = {"blink", "happy", "rest"}
PHRASES = {"我在。", "我在，陪你待会儿。", "嗯，接住了。", "慢慢来就好。", "安静待着，也很好。"}
FALLBACK = {"action": "happy", "text": "我在，陪你待会儿。", "source": "local"}

def validate_reply(value):
    if not isinstance(value, dict) or set(value) != {"action", "text"}:
        raise ValueError("reply schema")
    text = value["text"]
    if value["action"] not in ACTIONS or not isinstance(text, str):
        raise ValueError("reply type")
    if not text or len(text.encode("utf-8")) > 72 or any(ord(c) < 32 for c in text):
        raise ValueError("reply length")
    if text not in PHRASES:
        raise ValueError("unapproved phrase")
    # No diagnostic or punitive claims, including common equivalents.
    if any(w in text.lower() for w in ("焦虑", "抑郁", "诊断", "检测到", "不够努力", "anxiety", "depress", "diagnos")):
        raise ValueError("unsupported inference")
    return dict(value, source="agent")

def _request(summary):
    endpoint = os.getenv("PET_API_URL", "")
    key = os.getenv("PET_API_KEY", "")
    model = os.getenv("PET_MODEL", "")
    if not endpoint or not key or not model:
        return dict(FALLBACK)
    if not endpoint.startswith("https://"):
        return dict(FALLBACK)
    payload = {"model": model, "messages": [
        {"role": "system", "content": '你是温柔克制的像素伙伴。按键只是互动，不推断情绪、健康或人格，不责备不催促。只输出JSON，action从blink,happy,rest选择；text必须原样选自：'+json.dumps(sorted(PHRASES),ensure_ascii=False)},
        {"role": "user", "content": json.dumps(summary, ensure_ascii=False)}], "max_tokens": 120,
        "response_format": {"type": "json_object"}}
    if os.getenv("PET_DISABLE_THINKING") == "1":
        payload["thinking"] = {"type": "disabled"}
    request = urllib.request.Request(endpoint, data=json.dumps(payload).encode(), headers={"Authorization": "Bearer " + key, "Content-Type": "application/json"})
    try:
        deadline=time.monotonic()+8
        with urllib.request.urlopen(request, timeout=8) as response:
            raw=b""
            while len(raw)<=16384:
                if response.isclosed():
                    break
                remaining=deadline-time.monotonic()
                if remaining<=0:
                    raise TimeoutError("total deadline")
                response.fp.raw._sock.settimeout(remaining)
                chunk=response.read1(min(4096,16385-len(raw)))
                if not chunk:
                    break
                raw+=chunk
        if len(raw) > 16384:
            raise ValueError("response too large")
        content = json.loads(raw)["choices"][0]["message"]["content"]
        return validate_reply(json.loads(content))
    except Exception:
        # Never log request headers, keys, or provider response bodies.
        return dict(FALLBACK)

class Gate:
    def __init__(self):
        self.session = None
        self.epoch = 0
        self.last_window = -1
        self.last_call = float("-inf")
        self.quiet = True

    def accept(self, item, now):
        if not isinstance(item, dict):
            return False
        if item.get("type") == "hello" and item.get("protocol") == 2:
            if not isinstance(item.get("session"), str) or len(item["session"]) > 80:
                return False
            if type(item.get("epoch")) is not int or not 0 <= item["epoch"] <= 4294967295 or type(item.get("quiet")) is not bool:
                return False
            if item["session"] != self.session:
                self.last_window = -1
            self.session = item["session"]
            self.epoch = item.get("epoch", 0)
            self.quiet = item.get("quiet") is not False
            return False
        if item.get("type") != "rhythm" or item.get("protocol") != 2 or item.get("session") != self.session:
            return False
        if type(item.get("epoch")) is not int or item["epoch"] < self.epoch:
            return False
        if type(item.get("window")) is not int or item["window"] <= self.last_window:
            return False
        for key, maximum in (("presses",10000),("duration_ms",60000),("held_ms",100000000),("mean_interval_ms",10000)):
            if type(item.get(key)) is not int or not 0 <= item[key] <= maximum:
                return False
        self.epoch = item["epoch"]
        self.last_window = item["window"]
        self.quiet = item.get("quiet") is not False
        if self.quiet or item.get("candidate") is not True or item["presses"] < 3 or now-self.last_call < 60:
            return False
        self.last_call = now
        return True

def run_once(gate):
    import serial
    parser = argparse.ArgumentParser()
    parser.add_argument("--port", required=True)
    args = parser.parse_args()
    future = None
    context = None
    buffer = bytearray()
    discarding = False
    print("Bridge ready; configured=" + str(all(os.getenv(k) for k in ("PET_API_URL","PET_API_KEY","PET_MODEL"))), flush=True)
    with concurrent.futures.ThreadPoolExecutor(max_workers=1) as pool:
        with open_device(args.port, timeout=0.05, write_timeout=0.1) as port:
            port.write(b'{"type":"hello_request"}\n')
            while True:
                for byte in port.read(512):
                    if byte == 10:
                        if not discarding:
                            try:
                                item = json.loads(buffer)
                                if gate.accept(item,time.monotonic()) and future is None:
                                    context = (gate.session,gate.epoch,item["window"],time.monotonic())
                                    summary = {k:item[k] for k in ("presses","duration_ms","held_ms","mean_interval_ms")}
                                    future = pool.submit(respond,summary)
                                print(json.dumps(item,ensure_ascii=False),flush=True)
                            except (ValueError,UnicodeError):
                                pass
                        buffer.clear()
                        discarding=False
                    elif not discarding:
                        if len(buffer)>=1024:
                            buffer.clear(); discarding=True
                        else:
                            buffer.append(byte)
                if future is not None and future.done():
                    reply = future.result()
                    sid,epoch,window,started = context
                    if not gate.quiet and gate.session==sid and gate.epoch==epoch and time.monotonic()-started<12:
                        reply.update(type="reply",session=sid,epoch=epoch,window=window)
                        port.write((json.dumps(reply,ensure_ascii=False)+"\n").encode())
                        print("reply source="+reply["source"],flush=True)
                    future=None

def main():
    import serial
    gate=Gate()
    while True:
        try:
            run_once(gate)
        except (serial.SerialException, OSError):
            # Keep cooldown/dedup state across reconnect; discard in-flight replies.
            gate.quiet=True
            print("USB disconnected; retrying",flush=True)
            time.sleep(1)
        except KeyboardInterrupt:
            break

def respond(summary):
    if not all(os.getenv(k) for k in ("PET_API_URL","PET_API_KEY","PET_MODEL")):
        return dict(FALLBACK)
    try:
        # OS child enforces wall-clock deadline including DNS, headers and body.
        # subprocess.run kills and reaps timed-out children. At most one exists.
        result=subprocess.run([sys.executable,os.path.abspath(__file__),"--request"],input=json.dumps(summary),capture_output=True,text=True,timeout=8,check=True)
        value=json.loads(result.stdout)
        if value.get("source")=="agent":
            return validate_reply({"action":value.get("action"),"text":value.get("text")})
    except Exception:
        pass
    return dict(FALLBACK)

if __name__ == "__main__":
    if sys.argv[1:]==["--request"]:
        print(json.dumps(_request(json.loads(sys.stdin.read(2048))),ensure_ascii=True))
    else:
        main()
