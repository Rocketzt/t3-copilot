"""T3 Ops Copilot web server (stdlib only).

Serves the static UI in app/static and the JSON API described in CONTRACT.md section 8.
Run:  python app/server.py   (or run_app.bat)  ->  http://127.0.0.1:8803
Port: env T3_PORT (default 8803). Nothing here calls the network or a live model.
"""

from __future__ import annotations

import json
import os
import sys
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from urllib.parse import parse_qs, unquote, urlparse

ROOT = Path(__file__).resolve().parent.parent
STATIC = ROOT / "app" / "static"
sys.path.insert(0, str(ROOT))

from engine import pipeline  # noqa: E402

SIM = "模拟 / SIMULATED"
STATIC_FILES = {
    "/": "index.html",
    "/index.html": "index.html",
    "/app.js": "app.js",
    "/styles.css": "styles.css",
}
CONTENT_TYPES = {
    ".html": "text/html; charset=utf-8",
    ".js": "application/javascript; charset=utf-8",
    ".css": "text/css; charset=utf-8",
    ".svg": "image/svg+xml",
    ".png": "image/png",
    ".ico": "image/x-icon",
}


class Handler(BaseHTTPRequestHandler):
    server_version = "T3OpsCopilot/0.2"
    protocol_version = "HTTP/1.1"

    # ------------------------------------------------------------ plumbing
    def log_message(self, fmt, *args):  # keep the console ASCII-only
        try:
            msg = (fmt % args).encode("ascii", "replace").decode("ascii")
        except Exception:
            msg = "request"
        sys.stderr.write("%s - %s\n" % (self.address_string(), msg))

    def _send(self, status: int, body: bytes, content_type: str):
        self.send_response(status)
        self.send_header("Content-Type", content_type)
        self.send_header("Content-Length", str(len(body)))
        self.send_header("Cache-Control", "no-store")
        self.end_headers()
        try:
            self.wfile.write(body)
        except BrokenPipeError:
            pass

    def _json(self, status: int, payload):
        body = json.dumps(payload, ensure_ascii=False).encode("utf-8")
        self._send(status, body, "application/json; charset=utf-8")

    def _error(self, status: int, message: str, detail: str = ""):
        self._json(status, {"error": message, "detail": detail, "sim_label": SIM})

    def _body(self) -> dict:
        try:
            length = int(self.headers.get("Content-Length") or 0)
        except ValueError:
            length = 0
        if length <= 0:
            return {}
        raw = self.rfile.read(length)
        if not raw.strip():
            return {}
        try:
            value = json.loads(raw.decode("utf-8"))
        except (UnicodeDecodeError, json.JSONDecodeError) as exc:
            raise ValueError(f"invalid JSON body: {exc}") from exc
        if not isinstance(value, dict):
            raise ValueError("JSON body must be an object")
        return value

    def _static(self):
        parsed = urlparse(self.path)
        rel = STATIC_FILES.get(parsed.path)
        if rel is None:
            if parsed.path == "/favicon.ico":
                self._send(204, b"", "text/plain")
                return
            self._error(404, "not found", parsed.path)
            return
        path = STATIC / rel
        if not path.exists():
            self._error(500, "static file missing", rel)
            return
        ctype = CONTENT_TYPES.get(path.suffix, "text/plain; charset=utf-8")
        self._send(200, path.read_bytes(), ctype)

    # ------------------------------------------------------------ GET
    def do_GET(self):
        parsed = urlparse(self.path)
        path = parsed.path
        query = parse_qs(parsed.query)
        try:
            if path == "/api/health":
                self._json(200, pipeline.health())
            elif path == "/api/bootstrap":
                data = pipeline.bootstrap()
                data["runner_available"] = pipeline._runner_available()
                data["checker_available"] = pipeline._check_available()
                self._json(200, data)
            elif path == "/api/detector/ranking":
                self._json(200, pipeline.detector_ranking())
            elif path == "/api/detector/chart":
                raw = (query.get("airports") or [""])[0]
                airports = [unquote(a.strip()) for a in raw.split(",") if a.strip()] or None
                self._json(200, pipeline.chart(airports))
            elif path == "/api/network":
                year_raw = (query.get("year") or [""])[0].strip()
                month_raw = (query.get("month") or [""])[0].strip()
                if bool(year_raw) != bool(month_raw):
                    self._error(400, "provide both year and month, or neither")
                    return
                try:
                    year = int(year_raw) if year_raw else None
                    month = int(month_raw) if month_raw else None
                except ValueError:
                    self._error(400, "year and month must be integers")
                    return
                self._json(200, pipeline.network_view(year, month))
            elif path == "/api/detector/airport":
                name = unquote((query.get("name") or [""])[0]).strip()
                if not name:
                    self._error(400, "missing airport name")
                    return
                self._json(200, pipeline.detector_airport(name))
            elif path == "/api/feedback":
                self._json(200, {"records": pipeline.feedback_records(), "sim_label": SIM})
            elif path == "/api/export/sheet06":
                self._error(404, "endpoint cut from this build", "The filled Excel export is produced by scripts/build_excel_exports.py.")
            elif path.startswith("/api/"):
                self._error(404, "unknown endpoint", path)
            else:
                self._static()
        except Exception as exc:  # pragma: no cover
            self._error(500, "server error", str(exc))

    # ------------------------------------------------------------ POST
    def do_POST(self):
        path = urlparse(self.path).path
        try:
            body = self._body()
        except ValueError as exc:
            self._error(400, "bad request", str(exc))
            return
        try:
            if path == "/api/analyze":
                writer_mode = body.get("writer_mode") or "offline"
                if body.get("event_id"):
                    result = pipeline.analyze(str(body["event_id"]), writer_mode=writer_mode)
                elif body.get("custom") and isinstance(body["custom"], dict):
                    result = pipeline.analyze("CUSTOM", writer_mode=writer_mode, custom=body["custom"])
                else:
                    self._error(400, "provide event_id or custom")
                    return
                result["sim_label"] = SIM
                self._json(200, result)
            elif path == "/api/ask":
                question = str(body.get("question") or "").strip()
                if not question:
                    self._error(400, "missing question")
                    return
                writer_mode = body.get("writer_mode") or "offline"
                if body.get("event_id"):
                    result = pipeline.ask(question, str(body["event_id"]), writer_mode=writer_mode)
                elif body.get("custom") and isinstance(body["custom"], dict):
                    result = pipeline.ask(question, "CUSTOM", custom=body["custom"], writer_mode=writer_mode)
                else:
                    result = pipeline.ask(question, "EVT001", writer_mode=writer_mode)
                result["sim_label"] = SIM
                self._json(200, result)
            elif path == "/api/feedback":
                if not body.get("result"):
                    self._error(400, "missing feedback result")
                    return
                record = pipeline.add_feedback(body)
                self._json(200, {"record": record, "records": pipeline.feedback_records(), "sim_label": SIM})
            elif path == "/api/tests/run":
                result = pipeline.run_tests(writer_mode=str(body.get("writer_mode") or "offline"),
                                            include_own=bool(body.get("include_own", True)))
                result["sim_label"] = SIM
                self._json(200, result)
            elif path == "/api/checker/demo":
                event_id = str(body.get("event_id") or "EVT001")
                result = pipeline.run_bad_writer_demo(event_id)
                result["sim_label"] = SIM
                self._json(200, result)
            else:
                self._error(404, "unknown endpoint", path)
        except KeyError as exc:
            self._error(404, "not found", str(exc))
        except Exception as exc:  # pragma: no cover
            self._error(500, "server error", str(exc))


def main() -> int:
    port = int(os.environ.get("T3_PORT", "8803"))
    server = ThreadingHTTPServer(("127.0.0.1", port), Handler)
    print(f"T3 OPS COPILOT - SIMULATED - http://127.0.0.1:{port}")
    print("Press Ctrl+C to stop.")
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\nstopped")
    finally:
        server.server_close()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
