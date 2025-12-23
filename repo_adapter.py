# repo_adapter.py
from __future__ import annotations
from dataclasses import dataclass
from typing import List, Optional, Protocol, Dict, Any

from hair_salon_lab1_task9 import Client
from hair_salon_lab2 import ClientRepBase, ClientRepJson  # можно заменить на YAML/DBAdapter


class IClientRepository(Protocol):
    def list_all(self) -> List[Client]: ...
    def get(self, client_id: int) -> Optional[Client]: ...
    def create(self, payload: Dict[str, Any]) -> int: ...
    def update(self, client_id: int, payload: Dict[str, Any]) -> bool: ...
    def delete(self, client_id: int) -> bool: ...


@dataclass
class ClientRepoAdapter(IClientRepository):
    """
    Адаптер, чтобы контроллер работал с одним интерфейсом,
    а хранилище могло быть JSON/YAML/DB (через твои репозитории).
    """
    repo: ClientRepBase

    def list_all(self) -> List[Client]:
        self.repo.read_all()
        return list(self.repo.items)

    def get(self, client_id: int) -> Optional[Client]:
        self.repo.read_all()
        return self.repo.get_by_id(client_id)

    def create(self, payload: Dict[str, Any]) -> int:
        self.repo.read_all()
        c = Client({
            "first_name": payload["first_name"],
            "last_name": payload["last_name"],
            "father_name": payload["father_name"],
            "haircut_counter": int(payload["haircut_counter"]),
            "discount": int(payload["discount"]),
            "id": 0,  # будет переустановлен репозиторием
        })
        new_id = self.repo.add(c)
        if new_id is None:
            raise ValueError("Client not unique")
        return int(new_id)

    def update(self, client_id: int, payload: Dict[str, Any]) -> bool:
        self.repo.read_all()
        c = Client({
            "first_name": payload["first_name"],
            "last_name": payload["last_name"],
            "father_name": payload["father_name"],
            "haircut_counter": int(payload["haircut_counter"]),
            "discount": int(payload["discount"]),
            "id": int(client_id),
        })
        return bool(self.repo.replace_by_id(int(client_id), c))

    def delete(self, client_id: int) -> bool:
        self.repo.read_all()
        return bool(self.repo.delete_by_id(int(client_id)))


def build_repository() -> IClientRepository:
    # вариант 1: JSON (без БД)
    repo = ClientRepJson("data/clients.json")
    return ClientRepoAdapter(repo=repo)

    # вариант 2: если захочешь БД:
    # из hair_salon_lab2.py у тебя уже есть ClientRepDBAdapter (Adapter) :contentReference[oaicite:4]{index=4}
    # тогда build_repository будет возвращать адаптер вокруг ClientRepDBAdapter.
