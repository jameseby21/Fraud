"""Local-only dashboard. Run: python app.py"""
import json
import csv
import io
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from urllib.parse import parse_qs, urlsplit
from fraud import report
from casebook import load_catalog, mechanism_replay, public_replay
from quality import public_award_quality

ROOT = Path(__file__).resolve().parent


class Handler(BaseHTTPRequestHandler):
    def do_GET(self):
        parsed = urlsplit(self.path)
        path, query = parsed.path, parse_qs(parsed.query)
        filename = None
        try:
            if path in ("/api/report", "/api/export"):
                body = json.dumps(report(), indent=2).encode()
                kind = "application/json"
                if path == "/api/export":
                    filename = "synthetic-case-report.json"
            elif path == "/api/catalog":
                body = json.dumps(load_catalog(), indent=2).encode()
                kind = "application/json"
            elif path == "/api/quality":
                body = json.dumps(public_award_quality(ROOT), indent=2).encode()
                kind = "application/json"
                if query.get('download') == ['1']:
                    filename = 'public-award-quality.json'
            elif path == "/api/replay":
                case_id = query.get("case", [""])[0]
                mode = query.get("mode", ["mechanism"])[0]
                if mode == "mechanism":
                    result = mechanism_replay(case_id, int(query.get("step", ["0"])[0]))
                elif mode == "public":
                    result = public_replay(case_id, query.get("as_of", [""])[0])
                else:
                    raise ValueError("Unknown replay mode")
                body = json.dumps(result, indent=2).encode()
                kind = "application/json"
            elif path == "/api/data":
                rows = []
                csv_path = ROOT / "data" / "spending" / "awards.csv"
                if csv_path.exists():
                    rows = list(csv.DictReader(io.StringIO(csv_path.read_text(encoding="utf-8"))))
                provenance_path = ROOT / "data" / "spending" / "provenance.json"
                provenance = json.loads(provenance_path.read_text(encoding="utf-8")) if provenance_path.exists() else None
                attempts_path = ROOT / "data" / "intake_log.jsonl"
                attempts = [json.loads(line) for line in attempts_path.read_text(encoding="utf-8").splitlines()] if attempts_path.exists() else []
                body = json.dumps(dict(awards=rows, provenance=provenance, intake_attempts=attempts), indent=2).encode()
                kind = "application/json"
            elif path == "/api/download":
                files = {"cases": "data/cases.json", "evidence": "data/evidence.jsonl", "simulations": "data/synthetic_replays.jsonl",
                         "awards": "data/spending/awards.csv", "provenance": "data/spending/provenance.json", "intake": "data/intake_log.jsonl"}
                selected = query.get("name", [""])[0]
                if selected not in files:
                    raise KeyError(selected)
                target = ROOT / files[selected]
                body, kind, filename = target.read_bytes(), "application/octet-stream", target.name
            elif path == "/api/source":
                case_id = query.get("case", [""])[0]
                attempts = [json.loads(line) for line in (ROOT / "data" / "intake_log.jsonl").read_text(encoding="utf-8").splitlines()]
                matches = [a for a in attempts if a.get("case_id") == case_id and a["status"] == "downloaded"]
                if not matches:
                    raise KeyError(case_id)
                target = (ROOT / matches[-1]["artifact"]).resolve()
                if not target.is_relative_to((ROOT / "data" / "raw").resolve()):
                    raise ValueError("Invalid source artifact")
                body, kind, filename = target.read_bytes(), "application/octet-stream", target.name
            elif path in ("/", "/library", "/library.js", "/library.css"):
                names = {"/": ("index.html", "text/html; charset=utf-8"), "/library": ("library.html", "text/html; charset=utf-8"),
                         "/library.js": ("library.js", "text/javascript; charset=utf-8"), "/library.css": ("library.css", "text/css; charset=utf-8")}
                name, kind = names[path]
                body = (ROOT / "web" / name).read_bytes()
            else:
                self.send_error(404)
                return
        except KeyError:
            self.send_error(404, "Unknown case or download")
            return
        except (ValueError, TypeError):
            self.send_error(400, "Invalid replay parameters")
            return
        except OSError:
            self.send_error(503, "Local data unavailable; run python intake.py build")
            return
        self.send_response(200)
        self.send_header("Content-Type", kind)
        self.send_header("Content-Length", str(len(body)))
        self.send_header("Cache-Control", "no-store")
        self.send_header("X-Content-Type-Options", "nosniff")
        if filename:
            self.send_header("Content-Disposition", f'attachment; filename="{filename}"')
        self.end_headers()
        self.wfile.write(body)


if __name__ == "__main__":
    print("Fraud demo: http://127.0.0.1:8765 (Ctrl+C to stop)", flush=True)
    ThreadingHTTPServer(("127.0.0.1", 8765), Handler).serve_forever()
