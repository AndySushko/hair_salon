# edit_controller.py
from __future__ import annotations
from typing import Any, Dict, Optional, Tuple

import views
from repo_adapter import IClientRepository


class EditClientController:
    def __init__(self, repo: IClientRepository) -> None:
        self.repo = repo

    def edit_form(
        self,
        client_id: int,
        errors: Optional[dict] = None,
        values: Optional[dict] = None
    ) -> Tuple[int, str, str]:
        """
        GET: если values не передали — берём из репозитория
        POST fail: values передаются из payload, чтобы не терять ввод
        """
        if values is None:
            c = self.repo.get(client_id)
            if not c:
                return 404, "text/html; charset=utf-8", views.not_found_page(f"Клиент {client_id} не найден")
            values = c.to_dict()

        html = views.edit_client_page(client_id=client_id, errors=errors or {}, values=values or {})
        return 200, "text/html; charset=utf-8", html

    def validate(self, payload: Dict[str, Any]) -> Tuple[bool, dict, dict]:
        """
        Валидация строго в контроллере.
        Возвращает ok, cleaned, errors
        """
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
        # проверим существование, чтобы корректно вернуть 404
        existing = self.repo.get(client_id)
        if not existing:
            return 404, "text/html; charset=utf-8", views.not_found_page(f"Клиент {client_id} не найден")

        ok, cleaned, errors = self.validate(payload)
        if not ok:
            # отдаём форму с ошибками и введёнными значениями
            return self.edit_form(client_id, errors=errors, values={**payload, "id": client_id})

        # update: если репозиторий может вернуть False при конфликте/неуникальности
        updated_ok = self.repo.update(client_id, cleaned)
        if not updated_ok:
            errors["__all__"] = "Не удалось обновить (возможно, конфликт уникальности)"
            return self.edit_form(client_id, errors=errors, values={**payload, "id": client_id})

        html = views.edit_client_success_page(client_id)
        return 200, "text/html; charset=utf-8", html
