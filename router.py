# router.py
from __future__ import annotations
from dataclasses import dataclass
from typing import Callable, Optional, Tuple
from urllib.parse import urlparse

HandlerFn = Callable[..., object]


@dataclass
class Route:
    method: str
    path: str
    handler: HandlerFn


class Router:
    def __init__(self) -> None:
        self.routes: list[Route] = []

    def add(self, method: str, path: str, handler: HandlerFn) -> None:
        self.routes.append(Route(method=method.upper(), path=path, handler=handler))

    def match(self, method: str, raw_path: str) -> Tuple[Optional[HandlerFn], dict]:
        path = urlparse(raw_path).path
        method = method.upper()

        for r in self.routes:
            if r.method != method:
                continue

            if "<id>" not in r.path and r.path == path:
                return r.handler, {}

            if "<id>" in r.path:
                prefix, suffix = r.path.split("<id>")
                if path.startswith(prefix) and path.endswith(suffix):
                    mid = path[len(prefix):len(path) - len(suffix)]
                    if mid.isdigit():
                        return r.handler, {"id": int(mid)}

        return None, {}
