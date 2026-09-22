"""Synthetic single request probe. Prints only status, never credentials/body errors."""
import json
import os
import urllib.error
import urllib.request

def main():
    key=os.getenv("DEEPSEEK_API_KEY", "")
    print("key_present",bool(key))
    payload={"model":"deepseek-flash","messages":[{"role":"user","content":'Reply JSON only: {"action":"blink","text":"我在。"}'}],"max_tokens":120,"thinking":{"type":"disabled"},"response_format":{"type":"json_object"}}
    req=urllib.request.Request("https://api.deepseek.com/chat/completions",data=json.dumps(payload).encode(),headers={"Authorization":"Bearer "+key,"Content-Type":"application/json"})
    try:
        with urllib.request.urlopen(req,timeout=10) as response:
            result=json.load(response)
        print(json.dumps(result.get("choices",[]),ensure_ascii=True))
    except urllib.error.HTTPError as exc:
        print("http_status",exc.code)
    except Exception as exc:
        print(type(exc).__name__)

if __name__=="__main__":main()
