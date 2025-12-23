# controller.py
from __future__ import annotations
import json
from typing import Any, Dict, Optional, Tuple

from observer import Subject, SseObserver
from repo_adapter import IClientRepository
import views


class ClientController:
    def __init__(self, repo: IClientRepository) -> None:
        self.repo = repo
        self.subject = Subject()  # Subject по паттерну наблюдатель

    # ---------- HTML pages ----------
    def index(self) -> Tuple[int, str, str]:
        clients = self.repo.list_all()
        html = views.index_page(clients)
        return 200, "text/html; charset=utf-8", html

    def details(self, client_id: int) -> Tuple[int, str, str]:
        html = views.details_page(client_id)
        return 200, "text/html; charset=utf-8", html

    # ---------- API JSON ----------
    def api_get(self, client_id: int) -> Tuple[int, Dict[str, Any]]:
        c = self.repo.get(client_id)
        if not c:
            return 404, {"error": "not found"}
        return 200, c.to_dict()

    def api_create(self, payload: Dict[str, Any]) -> Tuple[int, Dict[str, Any]]:
        new_id = self.repo.create(payload)
        created = self.repo.get(new_id)
        data = created.to_dict() if created else {"id": new_id}
        # уведомим подписчиков “карточки” нового клиента (если уже кто-то подписан)
        self.subject.notify(str(new_id), "client", data)
        return 201, data

    def api_update(self, client_id: int, payload: Dict[str, Any]) -> Tuple[int, Dict[str, Any]]:
        ok = self.repo.update(client_id, payload)
        if not ok:
            return 409, {"error": "update failed (maybe not unique or not found)"}

        updated = self.repo.get(client_id)
        data = updated.to_dict() if updated else {"id": client_id}
        # ключевой момент: Наблюдатель — рассылка всем “окнам details”
        self.subject.notify(str(client_id), "client", data)
        return 200, data

    def api_delete(self, client_id: int) -> Tuple[int, Dict[str, Any]]:
        ok = self.repo.delete(client_id)
        if not ok:
            return 404, {"error": "not found"}

        self.subject.notify(str(client_id), "deleted", {"id": client_id})
        return 200, {"ok": True}

    # ---------- SSE subscribe (Observer) ----------
    def sse_subscribe(self, client_id: int, writer) -> None:
        key = str(client_id)

        obs = SseObserver(
            writer=writer,
            on_close=lambda: self.subject.detach(key, obs),
        )
        self.subject.attach(key, obs)

        # Сразу отправляем текущее состояние (инициализация карточки)
        c = self.repo.get(client_id)
        if c:
            obs.update("client", c.to_dict())
        else:
            obs.update("deleted", {"id": client_id})
