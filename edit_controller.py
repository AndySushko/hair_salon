# edit_controller.py
from __future__ import annotations
from typing import Any, Dict, Tuple

import views
from repo_adapter import IClientRepository


class EditClientController:
    def __init__(self, repo: IClientRepository) -> None:
        self.repo = repo

    def edit_form(self, client_id: int) -> Tuple[int, str, str]:
        c = self.repo.get(client_id)
        if not c:
            return 404, "text/html; charset=utf-8", views.not_found_page(f"Клиент {client_id} не найден")

        html = views.client_form_page(
            mode="edit",
            client_id=client_id,
            errors={},
            values=c.to_dict(),
            post_url=f"/clients/{client_id}/edit",
            success_event="updated",
        )
        return 200, "text/html; charset=utf-8", html

    def validate(self, payload: Dict[str, Any]) -> Tuple[bool, dict, dict]:
        errors: Dict[str, str] = {}
        cleaned: Dict[str, Any] = {}

        def req_str(key: str, max_len: int = 60) -> None:
            v = (payload.get(key) or "").strip()
            if not v:
                errors[key] = "Обязательное поле"
            elif len(v) > max_len:
                errors[key] = f"Слишком длинно (>{max_len})"
            else:
                cleaned[key] = v

        def req_int(key: str, min_v: int, max_v: int) -> None:
            raw = payload.get(key)
            try:
                v = int(raw)
            except Exception:
                errors[key] = "Должно быть целым числом"
                return
            if v < min_v or v > max_v:
                errors[key] = f"Допустимо {min_v}..{max_v}"
            else:
                cleaned[key] = v

        req_str("last_name")
        req_str("first_name")
        req_str("father_name")
        req_int("haircut_counter", 0, 10_000)
        req_int("discount", 0, 100)

        return (len(errors) == 0), cleaned, errors

    def update(self, client_id: int, payload: Dict[str, Any]) -> Tuple[int, str, str]:
        existing = self.repo.get(client_id)
        if not existing:
            return 404, "text/html; charset=utf-8", views.not_found_page(f"Клиент {client_id} не найден")

        ok, cleaned, errors = self.validate(payload)
        if not ok:
            html = views.client_form_page(
                mode="edit",
                client_id=client_id,
                errors=errors,
                values={**payload, "id": client_id},
                post_url=f"/clients/{client_id}/edit",
                success_event="updated",
            )
            return 200, "text/html; charset=utf-8", html

        updated_ok = self.repo.update(client_id, cleaned)
        if not updated_ok:
            html = views.client_form_page(
                mode="edit",
                client_id=client_id,
                errors={"__all__": "Не удалось обновить (возможно, конфликт уникальности)"},
                values={**payload, "id": client_id},
                post_url=f"/clients/{client_id}/edit",
                success_event="updated",
            )
            return 200, "text/html; charset=utf-8", html

        return 200, "text/html; charset=utf-8", views.form_success_page(
            event_type="updated",
            entity_id=client_id,
            text=f"Клиент #{client_id} обновлён."
        )
