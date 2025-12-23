# app.py
from __future__ import annotations
import os

from controller import ClientController
from repo_adapter import build_repository
from router import Router
from http_server import run


def build_router(ctrl: ClientController) -> Router:
    r = Router()
    # страницы
    r.add("GET", "/", lambda: ctrl.index())
    r.add("GET", "/clients/<id>", lambda id: ctrl.details(id))

    # API
    r.add("GET", "/api/clients/<id>", lambda id: (lambda code, data: (code, "application/json; charset=utf-8", __import__("json").dumps(data, ensure_ascii=False)))(*ctrl.api_get(id)))
    r.add("POST", "/api/clients", lambda payload: ctrl.api_create(payload))
    r.add("PUT", "/api/clients/<id>", lambda id, payload: ctrl.api_update(id, payload))
    r.add("DELETE", "/api/clients/<id>", lambda id: ctrl.api_delete(id))

    # Observer endpoint
    r.add("GET", "/api/clients/<id>/subscribe", lambda id, writer=None: None)  # match нужен
    return r


def main() -> None:
    os.makedirs("data", exist_ok=True)
    if not os.path.exists("data/clients.json"):
        with open("data/clients.json", "w", encoding="utf-8") as f:
            f.write("[]")

    repo = build_repository()
    ctrl = ClientController(repo)
    router = build_router(ctrl)

    # Router matcher мы отдадим handler, но http_server вызовет handler(params["id"], writer))
    def subscribe_handler(id: int, writer):
        return ctrl.sse_subscribe(id, writer)

    router.routes = [rt for rt in router.routes if rt.path != "/api/clients/<id>/subscribe"]
    router.add("GET", "/api/clients/<id>/subscribe", subscribe_handler)

    run("127.0.0.1", 8080, router)


if __name__ == "__main__":
    main()
