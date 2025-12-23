# app.py
from __future__ import annotations
import os

from controller import ClientController
from create_controller import NewClientController
from repo_adapter import build_repository
from router import Router
from http_server import run


def build_router(main_ctrl: ClientController, new_ctrl: NewClientController) -> Router:
    r = Router()

    # страницы
    r.add("GET", "/", lambda: main_ctrl.index())
    r.add("GET", "/clients/<id>", lambda id: main_ctrl.details(id))  # если details не нужен — можешь убрать
    r.add("GET", "/clients/new", lambda: new_ctrl.new_form())

    # создание (HTML ответ)
    r.add("POST", "/clients/new", lambda payload: new_ctrl.create(payload))

    # API (если у тебя есть эти методы в ClientController)
    r.add("POST", "/api/clients", lambda payload: main_ctrl.api_create(payload))
    r.add("GET", "/api/clients/<id>", lambda id: main_ctrl.api_get(id))
    r.add("PUT", "/api/clients/<id>", lambda id, payload: main_ctrl.api_update(id, payload))
    r.add("DELETE", "/api/clients/<id>", lambda id: main_ctrl.api_delete(id))
    r.add("GET", "/api/clients/<id>/subscribe", lambda id, writer=None: None)  # будет заменено ниже

    return r


def main() -> None:
    os.makedirs("data", exist_ok=True)

    # гарантируем корректный JSON (если файл пустой)
    path = "data/clients.json"
    if (not os.path.exists(path)) or os.path.getsize(path) == 0:
        with open(path, "w", encoding="utf-8") as f:
            f.write("[]")

    repo = build_repository()
    main_ctrl = ClientController(repo)
    new_ctrl = NewClientController(repo)

    router = build_router(main_ctrl, new_ctrl)

    # Реальный обработчик SSE subscribe
    def subscribe_handler(id: int, writer):
        return main_ctrl.sse_subscribe(id, writer)

    router.routes = [rt for rt in router.routes if rt.path != "/api/clients/<id>/subscribe"]
    router.add("GET", "/api/clients/<id>/subscribe", subscribe_handler)

    run("127.0.0.1", 8080, router)


if __name__ == "__main__":
    main()
