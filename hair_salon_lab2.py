import json
import os
from typing import List, Optional
import hair_salon_lab1_task9
from hair_salon_lab1_task9 import Client


class ClientRepJson:
    def __init__(self, file_path="clients.json"):
        self.file_path = file_path
        self.clients: List[Client] = []
        self.read_all()  # при создании сразу читаем данные из файла

    # a. Чтение всех значений из JSON файла (+)
    def read_all(self):
        try:
            if not os.path.exists(self.file_path):
                print("Файл не найден. Создан пустой список клиентов.")
                self.clients = []
                return

            with open(self.file_path, 'r', encoding='utf-8') as file:
                data = json.load(file)
                if data is None:
                    self.clients = []
                else:
                    self.clients = [Client(item) for item in data]

        except Exception as e:
            print(f"Ошибка при чтении файла: {e}")
            self.clients = []

    # b. Запись всех значений в JSON файл
    def write_all(self, file_name: str):
        try:
            with open(file_name, 'w', encoding='utf-8') as file:
                data = [client.to_dict() for client in self.clients]
                json.dump(data, file, indent=2, ensure_ascii=False)
        except Exception as e:
            print(f"Ошибка при записи в файл: {e}")

    # c. Получить объект по ID
    def get_by_id(self, client_id: int) -> Optional[Client]:
        if client_id >= 0:
            for client in self.clients:
                if client.get_id() == client_id:
                    return client
        return None

    # d. Получить список k по счёту n объектов (постранично)
    def get_k_n_short_list(self, k: int, n: int) -> List[Client]:
        if len(self.clients) >= n > 0 and (k <= len(self.clients) // n + 1) and k > 0:
            start = n * (k - 1)
            end = n * k
            return self.clients[start:end]
        return []

    # e. Сортировка по выбранному полю (+)
    def sort_by(self, param: str):
        match param:
            case 'id':  # Сортировка по id
                return self.clients.sort(key=lambda x: x.get_id())
            case 'haircut':  # Сортировка по количеству стрижек
                return self.clients.sort(key=lambda x: x.get_haircut_counter())
            case 'discount':    # Сортировка по скидке
                return self.clients.sort(key=lambda x: x.get_discount())
            case 'last_name':  # Сортировка по фамилии
                return self.clients.sort(key=lambda x: x.get_last_name())
        return self.clients[0:0]

    def _generate_new_id(self) -> int:
        """Возвращает следующий свободный id (максимальный + 1)."""
        if not self.clients:
            return 1
        return max(client.get_id() for client in self.clients) + 1

    def _is_unique(self, client: Client) -> bool:
        for c in self.clients:
            if c.get_last_name() == client.get_last_name() and c.get_haircut_counter() == client.get_haircut_counter():
                return False
        return True

    # f. Добавление нового объекта (при добавлении сформировать новый ID)
    def add_client(self, client: Client):
        if self._is_unique(client):
            client.set_id(self._generate_new_id())  # меняем id клиента на сформированный
            self.clients.append(client)
            self.write_all(self.file_path)

    # g. Замена элемента по ID
    def replace_by_id(self, client_id: int, new_client: Client) -> bool:
        if client_id >= 0 and self._is_unique(new_client):
            for i in range(len(self.clients)):
                if self.clients[i].get_id() == client_id:
                    self.clients[i] = new_client
                    self.clients[i].set_id(client_id)
                    self.write_all(self.file_path)
                    return True
        return False

    # h. Удаление элемента по ID
    def delete_by_id(self, client_id: int) -> bool:
        if client_id >= 0:
            for i in range(len(self.clients)):
                if self.clients[i].get_id() == client_id:
                    del self.clients[i]
                    self.write_all(self.file_path)
                    return True
        return False

    # i. Получить количество элементов
    def get_count(self) -> int:
        return len(self.clients)

    def print_all(self):
        """Вывод всех клиентов"""
        if not self.clients:
            print("Список клиентов пуст.")
            return

        for i, client in enumerate(self.clients):
            print(f"{i}: {client}")



# hair_salon_lab2_yaml.py

# Стрелки в диаграммах подписывать
import os
from typing import List, Optional

import yaml
import hair_salon_lab1_task9
from hair_salon_lab1_task9 import Client


class Client_rep_yaml:

    def __init__(self, file_path: str = "clients.yaml"):
        self.file_path = file_path
        self.clients: List[Client] = []
        self.read_all()

    # a. Чтение всех значений из файла
    def read_all(self) -> None:
        try:
            if not os.path.exists(self.file_path):
                print("Файл не найден. Создан пустой список клиентов.")
                self.clients = []
                return

            with open(self.file_path, "r", encoding="utf-8") as f:
                data = yaml.safe_load(f)

            if not data:
                self.clients = []
            else:
                # ожидаем список словарей
                self.clients = [Client(item) for item in data]

        except Exception as e:
            print(f"Ошибка при чтении YAML: {e}")
            self.clients = []

    # b. Запись всех значений в файл
    def write_all(self, file_name: Optional[str] = None) -> None:
        try:
            path = file_name or self.file_path
            data = [client.to_dict() for client in self.clients]
            with open(path, "w", encoding="utf-8") as f:
                yaml.safe_dump(
                    data,
                    f,
                    allow_unicode=True,
                    sort_keys=False,
                    indent=2,
                    default_flow_style=False,
                )
        except Exception as e:
            print(f"Ошибка при записи YAML: {e}")

    # c. Получить объект по ID
    def get_by_id(self, client_id: int) -> Optional[Client]:
        if client_id >= 0:
            for c in self.clients:
                if c.get_id() == client_id:
                    return c
        return None

    # d. get_k_n_short_list — получить список k-й страницы по n объектов
    #    (например, вторые 20 элементов => k=2, n=20)
    def get_k_n_short_list(self, k: int, n: int) -> List[Client]:
        if n <= 0 or k <= 0 or not self.clients:
            return []
        start = (k - 1) * n
        end = k * n
        if start >= len(self.clients):
            return []
        return self.clients[start:end]

    # e. Сортировать по выбранному полю
    # Поле предметной области: возьмём 'last_name' (фамилия).
    # Также поддержим те же ключи, что и в JSON-версии: id, haircut, discount, last_name
    def sort_by(self, param: str = "last_name") -> None:
        key_fn = None
        if param == "id":
            key_fn = lambda x: x.get_id()
        elif param == "haircut":
            key_fn = lambda x: x.get_haircut_counter()
        elif param == "discount":
            key_fn = lambda x: x.get_discount()
        elif param == "last_name":
            key_fn = lambda x: x.get_last_name()
        else:
            print(f"Неизвестный параметр сортировки '{param}'. Использую 'last_name'.")
            key_fn = lambda x: x.get_last_name()

        self.clients.sort(key=key_fn)

    # Внутренний помощник — сформировать новый ID
    def _generate_new_id(self) -> int:
        if not self.clients:
            return 1
        return max(c.get_id() for c in self.clients) + 1

    def _is_unique(self, client: Client) -> bool:
        for c in self.clients:
            if c.get_last_name() == client.get_last_name() and c.get_haircut_counter() == client.get_haircut_counter():
                return False
        return True

    # f. Добавить объект в список (сформировать новый ID)
    def add_client(self, client: Client) -> int:
        if self._is_unique(client):
            new_id = self._generate_new_id()
            client.set_id(new_id)
            self.clients.append(client)
            self.write_all()  # сохраняем в основной файл
            return new_id

    # g. Заменить элемент списка по ID
    def replace_by_id(self, client_id: int, new_client: Client) -> bool:
        if client_id >= 0:
            for i, c in enumerate(self.clients):
                if c.get_id() == client_id:
                    self.clients[i] = new_client
                    self.clients[i].set_id(client_id)  # ID должен сохраниться
                    self.write_all()
                    return True
        return False

    # h. Удалить элемент списка по ID
    def delete_by_id(self, client_id: int) -> bool:
        if client_id >= 0:
            for i, c in enumerate(self.clients):
                if c.get_id() == client_id:
                    del self.clients[i]
                    self.write_all()
                    return True
        return False

    # i. Получить количество элементов
    def get_count(self) -> int:
        return len(self.clients)

    # Удобно: распечатать всё
    def print_all(self) -> None:
        if not self.clients:
            print("Список клиентов пуст.")
            return
        for i, client in enumerate(self.clients):
            print(f"{i}: {client}")


# Доп. алиас в "кэмэл-кейсе", если понадобится
ClientRepYaml = Client_rep_yaml


if __name__ == "__main__":
    # Пример использования
    repo = Client_rep_yaml("clients.yaml")

    # b. Запись всех значений в файл (копию)
    repo.write_all("clients_copy.yaml")

    # c. Поиск по ID
    c = repo.get_by_id(3)
    if c:
        print("Найден клиент с id=3:", c)

    # d. Вторая страница по 20 элементов
    page = repo.get_k_n_short_list(k=2, n=20)
    print(f"Страница 2 (по 20): найдено {len(page)} эл.")

    # e. Сортировка по фамилии
    repo.sort_by("last_name")
    repo.print_all()

    # f. Добавление (ID генерируется)
    added = Client("Ivan", "Petrov", "Ivanovich", 3, 10, 5)
    new_id = repo.add_client(added)
    print("Добавлен клиент, id =", new_id)

    # g. Замена по id
    updated = Client("Petr", "Sidorov", "Petrovich", 7, 15, 10)
    print("Замена по id:", new_id, repo.replace_by_id(new_id, updated))

    # h. Удаление по id
    print("Удаление по id:", new_id, repo.delete_by_id(new_id))

    # i. Количество
    print("Всего клиентов:", repo.get_count())