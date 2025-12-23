# app.py
from __future__ import annotations
import os

from controller import ClientController
from create_controller import NewClientController
from edit_controller import EditClientController
from repo_adapter import build_repository
from router import Router
from http_server import run


def build_router(main_ctrl: ClientController,
                 new_ctrl: NewClientController,
                 edit_ctrl: EditClientController) -> Router:
    r = Router()

    # Главная страница
    r.add("GET", "/", lambda: main_ctrl.index())

    # Create window
    r.add("GET", "/clients/new", lambda: new_ctrl.new_form())
    r.add("POST", "/clients/new", lambda payload: new_ctrl.create(payload))

    # Edit window (новая вкладка)
    r.add("GET", "/clients/<id>/edit", lambda id: edit_ctrl.edit_form(id))
    r.add("POST", "/clients/<id>/edit", lambda payload, id: edit_ctrl.update(id, payload))

    # API для удаления (главная кнопка delete)
    r.add("DELETE", "/api/clients/<id>", lambda id: main_ctrl.api_delete(id))

    # (опционально) если у тебя реализован details через SSE — можешь оставить отдельно

    return r


def main() -> None:
    os.makedirs("data", exist_ok=True)
    path = "data/clients.json"
    if (not os.path.exists(path)) or os.path.getsize(path) == 0:
        with open(path, "w", encoding="utf-8") as f:
            f.write("[]")

    repo = build_repository()

    main_ctrl = ClientController(repo)
    new_ctrl = NewClientController(repo)
    edit_ctrl = EditClientController(repo)

    router = build_router(main_ctrl, new_ctrl, edit_ctrl)

    run("127.0.0.1", 8080, router)


if __name__ == "__main__":
    main()
