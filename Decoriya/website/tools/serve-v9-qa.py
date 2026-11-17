"""Local-only fixture: real delayed/error image responses for browser motion QA."""
from http.server import ThreadingHTTPServer, SimpleHTTPRequestHandler
from urllib.parse import urlsplit, parse_qs
from pathlib import Path
import time

ROOT=Path(__file__).resolve().parents[3]
class Handler(SimpleHTTPRequestHandler):
    def __init__(self,*args,**kwargs):
        super().__init__(*args,directory=str(ROOT),**kwargs)
    def do_GET(self):
        u=urlsplit(self.path)
        if '/assets/v9/' in u.path:
            q=parse_qs(u.query)
            if q.get('__qa_error')==['1']:
                self.send_error(503,'Fixture: image unavailable')
                return
            delay=min(3,max(0,float(q.get('__qa_delay',['0'])[0])))
            if delay:time.sleep(delay)
        super().do_GET()

if __name__=='__main__':
    print('Local v9 fixture at http://127.0.0.1:8795/Decoriya/website/v9/',flush=True)
    ThreadingHTTPServer(('127.0.0.1',8795),Handler).serve_forever()
