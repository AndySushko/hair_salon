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
        return self.clients[0:0]

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

    # f. Добавление нового объекта (при добавлении сформировать новый ID)
    def add_client(self, client: Client):
        client.set_id(self._generate_new_id())  # меняем id клиента на сформированный
        self.clients.append(client)
        self.write_all(self.file_path)

    # g. Замена элемента по ID
    def replace_by_id(self, client_id: int, new_client: Client) -> bool:
        if client_id >= 0:
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



# Пример использования
if __name__ == "__main__":

    # a. Чтение всех значений из JSON файла)
    repo = ClientRepJson("clients.json")

    # b. Запись всех значений в JSON файл
    repo.write_all('write_clients.json')

    # c. Получить объект по ID
    client = repo.get_by_id(3)
    if client:
        print(f"Найден клиент по id = 3: {client}")

    # d. Получить список k по счёту n объектов (постранично)
    pages = repo.get_k_n_short_list(3, 2)
    print(f"Получить список 2 по счёту 3 объектов (постранично)")
    for page in pages:
        print(f"  {page}")

    # e. Сортировка по выбранному полю
    repo.sort_by('haircut')
    print("\nПосле сортировки по количеству стрижек:")
    repo.print_all()

    # f. Добавить объект в список (при добавлении сформировать новый ID).
    added_client = Client('tname', 'tsurname', 'tfathername', 99, 99, 99)
    repo.add_client(added_client)
    print("\nПосле добавления клиента:")
    repo.print_all()

    # g. Заменить элемент списка по ID.
    replaced_client = Client('ttname', 'ttsurname', 'ttfathername', 98, 98, 98)
    replace_result = repo.replace_by_id(9, replaced_client)
    print(f"Получилось ли заменить по id(9):  {replace_result}")
    print("\nПосле замены клиента:")
    repo.print_all()

    # h. Удалить элемент списка по ID.
    del_result = repo.delete_by_id(9)
    print(f"Получилось ли удалить по id(9):  {del_result}")
    print("\nПосле удаления клиента:")
    repo.print_all()

    # i. Получить количество элементов
    client_count = repo.get_count()
    print(f"Количество клиентов: {client_count}")