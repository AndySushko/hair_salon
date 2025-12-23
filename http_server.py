# http_server.py
from __future__ import annotations
import json
import socket
from http.server import BaseHTTPRequestHandler, HTTPServer

from router import Router


class AppHandler(BaseHTTPRequestHandler):
    router: Router = None  # задаётся в run()

    def log_message(self, format, *args):
        # оставить стандартные логи, но без traceback-шумов
        print("%s - - [%s] %s" % (self.client_address[0], self.log_date_time_string(), format % args))

    def _send(self, code: int, content_type: str, body: bytes) -> None:
        try:
            self.send_response(code)
            self.send_header("Content-Type", content_type)
            self.send_header("Content-Length", str(len(body)))
            self.end_headers()
            self.wfile.write(body)
        except (ConnectionAbortedError, ConnectionResetError, BrokenPipeError, socket.error):
            # Клиент закрыл соединение — нормально (особенно на Windows)
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

        from static_files import MAIN_JS, DETAILS_JS, NEW_CLIENT_JS

        if name == "main.js":
            self._send(200, "application/javascript; charset=utf-8", MAIN_JS.encode("utf-8"))
            return True
        if name == "details.js":
            self._send(200, "application/javascript; charset=utf-8", DETAILS_JS.encode("utf-8"))
            return True
        if name == "new_client.js":
            self._send(200, "application/javascript; charset=utf-8", NEW_CLIENT_JS.encode("utf-8"))
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

        # SSE endpoint: handler сам пишет в wfile
        if self.path.endswith("/subscribe"):
            self.send_response(200)
            self.send_header("Content-Type", "text/event-stream; charset=utf-8")
            self.send_header("Cache-Control", "no-cache")
            self.send_header("Connection", "keep-alive")
            self.end_headers()

            def writer(b: bytes):
                try:
                    self.wfile.write(b)
                    self.wfile.flush()
                except (ConnectionAbortedError, ConnectionResetError, BrokenPipeError, socket.error):
                    pass

            handler(params["id"], writer)
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
        result = handler(payload, **params) if params else handler(payload)

        # HTML-ответ (code, ctype, body)
        if isinstance(result, tuple) and len(result) == 3:
            code, ctype, body = result
            self._send(code, ctype, body.encode("utf-8"))
            return

        # JSON-ответ (code, data)
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
