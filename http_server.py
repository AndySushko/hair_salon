# http_server.py
from __future__ import annotations
import json
import socket
from http.server import BaseHTTPRequestHandler, HTTPServer

from router import Router


class AppHandler(BaseHTTPRequestHandler):
    router: Router = None

    def log_message(self, format, *args):
        print("%s - - [%s] %s" % (self.client_address[0], self.log_date_time_string(), format % args))

    def _send(self, code: int, content_type: str, body: bytes) -> None:
        try:
            self.send_response(code)
            self.send_header("Content-Type", content_type)
            self.send_header("Content-Length", str(len(body)))
            self.end_headers()
            self.wfile.write(body)
        except (ConnectionAbortedError, ConnectionResetError, BrokenPipeError, socket.error):
            return

    def _read_json(self):
        length = int(self.headers.get("Content-Length", "0"))
        raw = self.rfile.read(length) if length else b"{}"
        try:
            return json.loads(raw.decode("utf-8"))
        except json.JSONDecodeError:
            return {}

    def _serve_static(self) -> bool:
        if not self.path.startswith("/static/"):
            return False

        name = self.path.replace("/static/", "", 1)
        from static_files import MAIN_JS, NEW_CLIENT_JS, EDIT_CLIENT_JS

        if name == "main.js":
            self._send(200, "application/javascript; charset=utf-8", MAIN_JS.encode("utf-8"))
            return True
        if name == "new_client.js":
            self._send(200, "application/javascript; charset=utf-8", NEW_CLIENT_JS.encode("utf-8"))
            return True
        if name == "edit_client.js":
            self._send(200, "application/javascript; charset=utf-8", EDIT_CLIENT_JS.encode("utf-8"))
            return True

        self._send(404, "text/plain; charset=utf-8", b"not found")
        return True

    def do_GET(self):
        if self.path == "/favicon.ico":
            self.send_response(204)
            self.end_headers()
            return

        if self._serve_static():
            return

        handler, params = self.router.match("GET", self.path)
        if not handler:
            self._send(404, "text/plain; charset=utf-8", b"not found")
            return

        result = handler(**params)
        code, ctype, body = result
        self._send(code, ctype, body.encode("utf-8"))

    def do_POST(self):
        handler, params = self.router.match("POST", self.path)
        if not handler:
            self._send(404, "text/plain; charset=utf-8", b"not found")
            return

        payload = self._read_json()

        # handler может ожидать payload + route params (id)
        result = handler(payload, **params) if params else handler(payload)

        # HTML-ответ
        if isinstance(result, tuple) and len(result) == 3:
            code, ctype, body = result
            self._send(code, ctype, body.encode("utf-8"))
            return

        # JSON-ответ
        code, data = result
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
