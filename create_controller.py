# create_controller.py
from __future__ import annotations
from typing import Any, Dict, Tuple

import views
from repo_adapter import IClientRepository


class NewClientController:
    def __init__(self, repo: IClientRepository) -> None:
        self.repo = repo

    def new_form(self) -> Tuple[int, str, str]:
        # пустая форма — логика контроллера (values пустые)
        html = views.client_form_page(
            mode="create",
            client_id=None,
            errors={},
            values={},
            post_url="/clients/new",
            success_event="created",
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

    def create(self, payload: Dict[str, Any]) -> Tuple[int, str, str]:
        ok, cleaned, errors = self.validate(payload)
        if not ok:
            html = views.client_form_page(
                mode="create",
                client_id=None,
                errors=errors,
                values=payload,
                post_url="/clients/new",
                success_event="created",
            )
            return 200, "text/html; charset=utf-8", html

        try:
            new_id = self.repo.create(cleaned)
        except ValueError:
            html = views.client_form_page(
                mode="create",
                client_id=None,
                errors={"__all__": "Такой клиент уже существует (не уникален)"},
                values=payload,
                post_url="/clients/new",
                success_event="created",
            )
            return 200, "text/html; charset=utf-8", html

        return 201, "text/html; charset=utf-8", views.form_success_page(
            event_type="created",
            entity_id=new_id,
            text=f"Клиент создан. ID: {new_id}"
        )
