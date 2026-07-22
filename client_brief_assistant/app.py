#!/usr/bin/env python3
"""Run the Grounded Client Brief Assistant with no third-party dependencies."""

from __future__ import annotations

import argparse
import json
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from urllib.parse import urlparse

from src.service import ApprovalRequiredError, BriefService, RequestValidationError


ROOT = Path(__file__).resolve().parent
STATIC = ROOT / "static"
SERVICE = BriefService(ROOT / "data" / "synthetic_records.json")
STATIC_FILES = {
    "/": (STATIC / "index.html", "text/html; charset=utf-8"),
    "/app.js": (STATIC / "app.js", "text/javascript; charset=utf-8"),
    "/styles.css": (STATIC / "styles.css", "text/css; charset=utf-8"),
}


class Handler(BaseHTTPRequestHandler):
    server_version = "GroundedBriefDemo/1.0"

    def _send(self, status: int, body: bytes, content_type: str) -> None:
        self.send_response(status)
        self.send_header("Content-Type", content_type)
        self.send_header("Content-Length", str(len(body)))
        self.send_header("Cache-Control", "no-store")
        self.send_header("X-Content-Type-Options", "nosniff")
        self.send_header("Referrer-Policy", "no-referrer")
        self.end_headers()
        self.wfile.write(body)

    def _json(self, status: int, payload: dict) -> None:
        self._send(status, json.dumps(payload, ensure_ascii=True).encode(), "application/json; charset=utf-8")

    def _read_json(self) -> dict:
        try:
            length = int(self.headers.get("Content-Length", "0"))
        except ValueError as error:
            raise RequestValidationError("Invalid Content-Length.") from error
        if length <= 0 or length > 64_000:
            raise RequestValidationError("Request body is missing or too large.")
        try:
            return json.loads(self.rfile.read(length))
        except json.JSONDecodeError as error:
            raise RequestValidationError("Malformed JSON request.") from error

    def do_GET(self) -> None:  # noqa: N802 - required by BaseHTTPRequestHandler
        path = urlparse(self.path).path
        if path == "/api/clients":
            self._json(200, {"clients": SERVICE.clients(), "synthetic": True})
            return
        static_file = STATIC_FILES.get(path)
        if static_file and static_file[0].is_file():
            self._send(200, static_file[0].read_bytes(), static_file[1])
            return
        self._json(404, {"error": "Not found."})

    def do_POST(self) -> None:  # noqa: N802 - required by BaseHTTPRequestHandler
        path = urlparse(self.path).path
        try:
            payload = self._read_json()
            if path == "/api/analyze":
                self._json(200, SERVICE.analyze(payload))
            elif path == "/api/export":
                self._json(200, SERVICE.export(payload))
            else:
                self._json(404, {"error": "Not found."})
        except ApprovalRequiredError as error:
            self._json(403, {"error": str(error), "category": "approval_required"})
        except RequestValidationError as error:
            self._json(400, {"error": str(error), "category": "invalid_input"})
        except Exception:
            self._json(500, {"error": "Unexpected server error.", "category": "internal_error"})

    def log_message(self, format_string: str, *args) -> None:
        # Avoid logging request content. Keep only the default path/status metadata.
        super().log_message(format_string, *args)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--host", default="127.0.0.1")
    parser.add_argument("--port", type=int, default=8765)
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    server = ThreadingHTTPServer((args.host, args.port), Handler)
    print(f"Grounded Client Brief Assistant: http://{args.host}:{args.port}")
    print("Synthetic data only. Press Ctrl+C to stop.")
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        pass
    finally:
        server.server_close()


if __name__ == "__main__":
    main()
