# repositories.py
from __future__ import annotations
from abc import ABC, abstractmethod
from typing import List, Optional
import os
import json
import yaml

from hair_salon_lab1_task9 import Client


class ClientRepBase(ABC):
    def __init__(self, file_path: str):
        self.file_path = file_path
        self.items: List[Client] = []
        self.read_all()

    # a. Чтение всех значений из файла
    def read_all(self) -> None:
        if not os.path.exists(self.file_path):
            self.items = []
            return
        raw = self._load_from_storage()
        self.items = [Client(d) for d in (raw or [])]

    # b. Запись всех значений в файл
    def write_all(self, file_name: Optional[str] = None) -> None:
        data = [c.to_dict() for c in self.items]
        self._dump_to_storage(data, file_name=file_name)

    # c. Получить объект по ID
    def get_by_id(self, client_id: int) -> Optional[Client]:
        if client_id >= 0:
            for client in self.items:
                if client.get_id() == client_id:
                    return client
        return None

    # d. Пагинация: k-я страница по n элементов
    def get_k_n_short_list(self, k: int, n: int) -> List[Client]:
        if len(self.items) >= n > 0 and (k <= len(self.items) // n + 1) and k > 0:
            start = n * (k - 1)
            end = n * k
            return self.items[start:end]
        return []

    # e. Сортировка по выбранному полю (по умолчанию по кол-ву стрижек)
    def sort_by(self, param: str = "get_haircut_counter") -> None:
        key_map = {
            "id": lambda x: x.get_id(),
            "haircut": lambda x: x.get_haircut_counter(),
            "discount": lambda x: x.get_discount(),
            "last_name": lambda x: x.get_last_name(),
        }
        key_fn = key_map.get(param, key_map["last_name"])
        self.items.sort(key=key_fn)

    def _is_unique(self, client: Client) -> bool:
        for c in self.items:
            if c.get_last_name() == client.get_last_name() and c.get_haircut_counter() == client.get_haircut_counter():
                return False
        return True

    # f. Добавить объект (сформировать новый ID)
    def add(self, client: Client):
        if self._is_unique(client):
            new_id = self._generate_new_id()
            client.set_id(new_id)
            self.items.append(client)
            self.write_all()
            return new_id

    # g. Заменить по ID
    def replace_by_id(self, client_id: int, new_client: Client) -> bool:
        if client_id >= 0 and self._is_unique(new_client):
            for i, c in enumerate(self.items):
                if c.get_id() == client_id:
                    new_client.set_id(client_id)
                    self.items[i] = new_client
                    self.write_all()
                    return True
        return False

    # h. Удалить по ID
    def delete_by_id(self, client_id: int) -> bool:
        for i, c in enumerate(self.items):
            if c.get_id() == client_id:
                del self.items[i]
                self.write_all()
                return True
        return False

    # i. Кол-во элементов
    def get_count(self) -> int:
        return len(self.items)

    def _generate_new_id(self) -> int:
        return (max((c.get_id() for c in self.items), default=0) + 1)

    def print_all(self):
        """Вывод всех клиентов"""
        if not self.items:
            print("Список клиентов пуст.")
            return

        for i, client in enumerate(self.items):
            print(f"{i}: {client}")

    # Абстрактные «крючки» для формата хранения
    @abstractmethod
    def _load_from_storage(self) -> List[dict]:
        ...

    @abstractmethod
    def _dump_to_storage(self, data: List[dict], file_name: Optional[str] = None) -> None:
        ...


class ClientRepJson(ClientRepBase):
    def __init__(self, file_path: str = "clients.json"):
        super().__init__(file_path)

    def _load_from_storage(self) -> List[dict]:
        with open(self.file_path, "r", encoding="utf-8") as f:
            return json.load(f) or []

    def _dump_to_storage(self, data: List[dict], file_name: Optional[str] = None) -> None:
        path = file_name or self.file_path
        with open(path, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=2)



class ClientRepYaml(ClientRepBase):
    def __init__(self, file_path: str = "clients.yaml"):
        super().__init__(file_path)

    def _load_from_storage(self) -> List[dict]:
        with open(self.file_path, "r", encoding="utf-8") as f:
            data = yaml.safe_load(f)
            return data or []

    def _dump_to_storage(self, data: List[dict], file_name: Optional[str] = None) -> None:
        path = file_name or self.file_path
        with open(path, "w", encoding="utf-8") as f:
            yaml.safe_dump(
                data,
                f,
                allow_unicode=True,
                sort_keys=False,
                indent=2,
                default_flow_style=False,
            )

# Пример использования
repo = ClientRepJson("clients2.json")

# b. Запись всех значений в файл (копию)
repo.write_all("clients_copy.yaml")

# c. Поиск по ID
c = repo.get_by_id(3)
if c:
    print("Найден клиент с id=3:", c)


# d. Получить список k по счёту n объектов (постранично)
pages = repo.get_k_n_short_list(2, 4)
print(f"Получить список 2 по счёту 3 объектов (постранично)")
for page in pages:
    print(f"  {page}")

# e. Сортировка по фамилии
repo.sort_by("id")
repo.print_all()

# f. Добавление (ID генерируется)
added = Client("Ivan", "Petrov", "Ivanovich", 3, 10, 5)
new_id = repo.add(added)
print("Добавлен клиент, id =", new_id)
repo.print_all()

# g. Замена по id
updated = Client("Petr", "Sidorov", "Petrovich", 7, 15, 10)
print("Замена по id:", new_id, repo.replace_by_id(new_id, updated))
repo.print_all()

# h. Удаление по id
print("Удаление по id:", new_id, repo.delete_by_id(new_id))
repo.print_all()

# i. Количество
print("Всего клиентов:", repo.get_count())