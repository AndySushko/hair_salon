# http_server.py
from __future__ import annotations
import json
from http.server import BaseHTTPRequestHandler, HTTPServer
from urllib.parse import parse_qs
import socket

from router import Router


class AppHandler(BaseHTTPRequestHandler):
    router: Router = None  # будет проставлено в app.py


    def _send(self, code: int, content_type: str, body: bytes) -> None:
        try:
            self.send_response(code)
            self.send_header("Content-Type", content_type)
            self.send_header("Content-Length", str(len(body)))
            self.end_headers()
            self.wfile.write(body)
        except (ConnectionAbortedError, ConnectionResetError, BrokenPipeError, socket.error):
            # Клиент (браузер) закрыл соединение — это нормально, просто не пишем traceback
            return

    def _read_json(self):
        length = int(self.headers.get("Content-Length", "0"))
        raw = self.rfile.read(length) if length else b"{}"
        return json.loads(raw.decode("utf-8"))

    # static files (простая раздача)
    def _serve_static(self) -> bool:
        if not self.path.startswith("/static/"):
            return False
        name = self.path.replace("/static/", "", 1)
        if name == "main.js":
            from static_files import MAIN_JS
            self._send(200, "application/javascript; charset=utf-8", MAIN_JS.encode("utf-8"))
            return True
        if name == "details.js":
            from static_files import DETAILS_JS
            self._send(200, "application/javascript; charset=utf-8", DETAILS_JS.encode("utf-8"))
            return True
        self._send(404, "text/plain; charset=utf-8", b"not found")
        return True

    def do_GET(self):
        if self._serve_static():
            return

        handler, params = self.router.match("GET", self.path)
        if not handler:
            self._send(404, "text/plain; charset=utf-8", b"not found")
            return

        # SSE endpoint: handler сам пишет в wfile, не через _send
        if self.path.endswith("/subscribe"):
            self.send_response(200)
            self.send_header("Content-Type", "text/event-stream; charset=utf-8")
            self.send_header("Cache-Control", "no-cache")
            self.send_header("Connection", "keep-alive")
            self.end_headers()

            def writer(b: bytes):
                self.wfile.write(b)
                self.wfile.flush()

            handler(params["id"], writer)
            return

        result = handler(**params)
        code, ctype, body = result
        self._send(code, ctype, body.encode("utf-8"))

    def do_POST(self):
        handler, _ = self.router.match("POST", self.path)
        if not handler:
            self._send(404, "text/plain; charset=utf-8", b"not found")
            return
        payload = self._read_json()
        code, data = handler(payload)
        self._send(code, "application/json; charset=utf-8", json.dumps(data, ensure_ascii=False).encode("utf-8"))

    def do_PUT(self):
        handler, params = self.router.match("PUT", self.path)
        if not handler:
            self._send(404, "text/plain; charset=utf-8", b"not found")
            return
        payload = self._read_json()
        code, data = handler(params["id"], payload)
        self._send(code, "application/json; charset=utf-8", json.dumps(data, ensure_ascii=False).encode("utf-8"))

    def do_DELETE(self):
        handler, params = self.router.match("DELETE", self.path)
        if not handler:
            self._send(404, "text/plain; charset=utf-8", b"not found")
            return
        code, data = handler(params["id"])
        self._send(code, "application/json; charset=utf-8", json.dumps(data, ensure_ascii=False).encode("utf-8"))


def run(host: str, port: int, router: Router) -> None:
    AppHandler.router = router
    HTTPServer((host, port), AppHandler).serve_forever()
