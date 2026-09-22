import json
import os
import socket
import threading
import time
import unittest
from unittest.mock import patch
import companion as c

class CompanionTests(unittest.TestCase):
    def test_phrases(self):
        for phrase in c.PHRASES:
            self.assertEqual(c.validate_reply(dict(action="blink",text=phrase))["source"],"agent")
        for phrase in ("你现在很难过。","你太懒了，快来陪我。","x"*80):
            with self.assertRaises(ValueError):
                c.validate_reply(dict(action="happy",text=phrase))

    def test_bad_hello(self):
        gate=c.Gate()
        for value in ({},"bad",True,-1,2**32):
            self.assertFalse(gate.accept(dict(type="hello",protocol=2,session="s",epoch=value,quiet=False),0))
            self.assertIsNone(gate.session)

    def test_gate(self):
        gate=c.Gate();gate.accept(dict(type="hello",protocol=2,session="s",epoch=0,quiet=False),0)
        row=dict(type="rhythm",protocol=2,session="s",epoch=0,quiet=False,window=1,presses=3,duration_ms=10000,held_ms=300,mean_interval_ms=100,candidate=True)
        self.assertTrue(gate.accept(row,0))
        self.assertFalse(gate.accept(row,60))
        row["window"]=2;self.assertFalse(gate.accept(row,59))
        row["window"]=3;self.assertTrue(gate.accept(row,60))
        gate.accept(dict(type="hello",protocol=2,session="s",epoch=1,quiet=True),61)
        row["window"]=4;self.assertFalse(gate.accept(row,120))

    def test_no_key(self):
        with patch.dict(os.environ,{},clear=True):
            self.assertEqual(c.respond({})["source"],"local")

    def test_real_stalled_tls_process_deadline(self):
        # Local socket accepts but never completes TLS. No external service.
        listener=socket.socket();listener.bind(("127.0.0.1",0));listener.listen(1)
        stop=threading.Event()
        def serve():
            conn,_=listener.accept()
            with conn:stop.wait(12)
        thread=threading.Thread(target=serve,daemon=True);thread.start()
        try:
            env={"PET_API_URL":f"https://127.0.0.1:{listener.getsockname()[1]}/chat/completions","PET_API_KEY":"synthetic-only","PET_MODEL":"fixture"}
            with patch.dict(os.environ,env):
                started=time.monotonic();result=c.respond({"presses":3});elapsed=time.monotonic()-started
            self.assertEqual(result["source"],"local")
            self.assertLess(elapsed,10)
            self.assertGreater(elapsed,7)
        finally:
            stop.set();listener.close();thread.join(2)

if __name__=="__main__":unittest.main()
