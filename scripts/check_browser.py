"""Run optional local browser QA against an isolated server, then shut it down."""
import subprocess
import sys
import threading
from http.server import ThreadingHTTPServer
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from app import Handler


class QuietHandler(Handler):
    def log_message(self, *args):
        pass


if __name__ == '__main__':
    server = ThreadingHTTPServer(('127.0.0.1', 0), QuietHandler)
    thread = threading.Thread(target=server.serve_forever, daemon=True)
    thread.start()
    try:
        result = subprocess.run(['node', str(ROOT / 'scripts' / 'browser_smoke.mjs'),
                                 'http://127.0.0.1:' + str(server.server_port)], cwd=ROOT, timeout=90)
    finally:
        server.shutdown()
        server.server_close()
        thread.join(timeout=3)
    raise SystemExit(result.returncode)
