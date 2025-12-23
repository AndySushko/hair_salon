from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Any, Callable, List, Optional
import json
import os

import psycopg2
from psycopg2 import sql
import yaml

from hair_salon_lab1_task9 import Client


class ClientRepBase(ABC):
    def __init__(self, file_path: str) -> None:
        self.file_path = file_path
        self.items: List[Client] = []
        self.read_all()

    # a. Чтение всех значений из файла / хранилища
    def read_all(self) -> None:
        if not os.path.exists(self.file_path):
            self.items = []
            return
        raw = self._load_from_storage()
        self.items = [Client(d) for d in (raw or [])]

    # b. Запись всех значений в файл / хранилище
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

    # e. Сортировка по выбранному полю (по умолчанию по фамилии)
    def sort_by(self, param: str = "last_name") -> None:
        key_map = {
            "id": lambda x: x.get_id(),
            "haircut": lambda x: x.get_haircut_counter(),
            "discount": lambda x: x.get_discount(),
            "last_name": lambda x: x.get_last_name(),
        }
        key_fn = key_map.get(param, key_map["last_name"])
        self.items.sort(key=key_fn)

    def _is_unique(self, client: Client) -> bool:
        """Проверка уникальности клиента по (фамилия, количество стрижек)."""
        for c in self.items:
            if (
                c.get_last_name() == client.get_last_name()
                and c.get_haircut_counter() == client.get_haircut_counter()
            ):
                return False
        return True

    # f. Добавить объект (сформировать новый ID)
    def add(self, client: Client) -> Optional[int]:
        if self._is_unique(client):
            new_id = self._generate_new_id()
            client.set_id(new_id)
            self.items.append(client)
            self.write_all()
            return new_id
        return None

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
        return max((c.get_id() for c in self.items), default=0) + 1

    def print_all(self) -> None:
        """Вывод всех клиентов."""
        if not self.items:
            print("Список клиентов пуст.")
            return

        for i, client in enumerate(self.items):
            print(f"{i}: {client}")

    # Абстрактные «крючки» для формата хранения
    @abstractmethod
    def _load_from_storage(self) -> List[dict]:
        raise NotImplementedError

    @abstractmethod
    def _dump_to_storage(
        self,
        data: List[dict],
        file_name: Optional[str] = None,
    ) -> None:
        raise NotImplementedError


class ClientRepJson(ClientRepBase):
    def __init__(self, file_path: str = "clients.json") -> None:
        super().__init__(file_path)

    def _load_from_storage(self) -> List[dict]:
        with open(self.file_path, "r", encoding="utf-8") as f:
            return json.load(f) or []

    def _dump_to_storage(
        self,
        data: List[dict],
        file_name: Optional[str] = None,
    ) -> None:
        path = file_name or self.file_path
        with open(path, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=2)


class ClientRepYaml(ClientRepBase):
    def __init__(self, file_path: str = "clients.yaml") -> None:
        super().__init__(file_path)

    def _load_from_storage(self) -> List[dict]:
        with open(self.file_path, "r", encoding="utf-8") as f:
            data = yaml.safe_load(f)
            return data or []

    def _dump_to_storage(
        self,
        data: List[dict],
        file_name: Optional[str] = None,
    ) -> None:
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


class DatabaseConnection:
    """Одиночка для работы с PostgreSQL."""

    _instance: Optional["DatabaseConnection"] = None

    def __init__(self, dsn: str) -> None:
        self.dsn = dsn
        self.conn = psycopg2.connect(dsn)

    @classmethod
    def get_instance(cls, dsn: str) -> "DatabaseConnection":
        """
        Возвращает единственный экземпляр соединения с БД.
        Если соединение ещё не создано — создаёт его.
        """
        if cls._instance is None:
            cls._instance = cls(dsn)
        return cls._instance

    def get_connection(self):
        """Вернуть объект соединения psycopg2."""
        return self.conn

    def close(self) -> None:
        """Закрыть соединение и сбросить одиночку."""
        if self.conn is not None:
            self.conn.close()
            self.conn = None
        DatabaseConnection._instance = None


class ClientRepDB:
    def __init__(self, db: DatabaseConnection) -> None:
        # Делегируем работу с соединением объекту-одиночке
        self.db = db

    @property
    def conn(self) -> psycopg2.extensions.connection:
        return self.db.get_connection()

    # Преобразование строки из БД в dict для Client(d).
    def _row_to_dict(self, row: Any) -> dict:
        return {
            "first_name": row[1],
            "last_name": row[2],
            "father_name": row[3],
            "haircut_counter": row[4],
            "discount": row[5],
            "id": row[0],
        }

    # a. Получить объект по ID
    def get_by_id(self, client_id: int) -> Optional[Client]:
        if client_id < 0:
            return None

        with self.conn.cursor() as cur:
            cur.execute(
                """
                SELECT id, first_name, last_name, father_name,
                       haircut_counter, discount
                FROM clients
                WHERE id = %s
                """,
                (client_id,),
            )
            row = cur.fetchone()

        if row is None:
            return None

        return Client(self._row_to_dict(row))

    # b. get_k_n_short_list: Получить список k по счету n объектов
    def get_k_n_short_list(self, k: int, n: int) -> List[Client]:
        if n <= 0 or k <= 0:
            return []

        offset = (k - 1) * n

        with self.conn.cursor() as cur:
            cur.execute(
                """
                SELECT id, first_name, last_name, father_name,
                       haircut_counter, discount
                FROM clients
                ORDER BY id
                LIMIT %s OFFSET %s
                """,
                (n, offset),
            )
            rows = cur.fetchall()

        return [Client(self._row_to_dict(r)) for r in rows]

    # c. Добавить объект в список (при добавлении сформировать новый ID)
    def add(self, client: Client) -> int:
        # ID генерируется автоматически в БД (SERIAL)
        with self.conn:
            with self.conn.cursor() as cur:
                cur.execute(
                    """
                    INSERT INTO clients
                        (first_name, last_name, father_name,
                         haircut_counter, discount)
                    VALUES (%s, %s, %s, %s, %s)
                    RETURNING id
                    """,
                    (
                        client.get_first_name(),
                        client.get_last_name(),
                        client.get_father_name(),
                        client.get_haircut_counter(),
                        client.get_discount(),
                    ),
                )
                new_id = cur.fetchone()[0]

        return new_id

    # d. Заменить элемент списка по ID
    def replace_by_id(self, client_id: int, new_client: Client) -> bool:
        if client_id < 0:
            return False

        with self.conn:
            with self.conn.cursor() as cur:
                cur.execute(
                    """
                    UPDATE clients
                    SET first_name = %s,
                        last_name = %s,
                        father_name = %s,
                        haircut_counter = %s,
                        discount = %s
                    WHERE id = %s
                    """,
                    (
                        new_client.get_first_name(),
                        new_client.get_last_name(),
                        new_client.get_father_name(),
                        new_client.get_haircut_counter(),
                        new_client.get_discount(),
                        client_id,
                    ),
                )
                updated = cur.rowcount > 0

        return updated

    # e. Удалить элемент списка по ID
    def delete_by_id(self, client_id: int) -> bool:
        if client_id < 0:
            return False

        with self.conn:
            with self.conn.cursor() as cur:
                cur.execute(
                    "DELETE FROM clients WHERE id = %s",
                    (client_id,),
                )
                deleted = cur.rowcount > 0

        return deleted

    # f. get_count: Получить количество элементов
    def get_count(self) -> int:
        with self.conn.cursor() as cur:
            cur.execute("SELECT COUNT(*) FROM clients")
            count = cur.fetchone()[0]
        return count

    def close(self) -> None:
        """Закрываем соединение через одиночку."""
        self.db.close()

    def get_all(self) -> List[Client]:
        with self.conn.cursor() as cur:
            cur.execute(
                """
                SELECT id, first_name, last_name, father_name,
                       haircut_counter, discount
                FROM clients
                ORDER BY id
                """
            )
            rows = cur.fetchall()

        return [Client(self._row_to_dict(r)) for r in rows]

    def print_all(self) -> None:
        """Красивый вывод клиентов из БД."""
        clients = self.get_all()

        if not clients:
            print("Список клиентов пуст.")
            return

        print("\n" + "=" * 60)
        print(
            f"{'ID':<4} {'Фамилия':<15} {'Имя':<12} "
            f"{'Отчество':<15} {'Стрижки':<8} {'Скидка':<6}"
        )
        print("-" * 60)

        for client in clients:
            print(
                f"{client.get_id():<4} "
                f"{client.get_last_name():<15} "
                f"{client.get_first_name():<12} "
                f"{client.get_father_name():<15} "
                f"{client.get_haircut_counter():<8} "
                f"{client.get_discount():<6}%"
            )
        print("=" * 60)

    def clear_all(self) -> bool:
        """Очистить таблицу clients."""
        try:
            with self.conn:
                with self.conn.cursor() as cur:
                    cur.execute("TRUNCATE TABLE clients RESTART IDENTITY CASCADE;")
                    print("Таблица clients очищена.")
                    return True
        except Exception as exc:  # noqa: BLE001
            print(f"Ошибка при очистке таблицы: {exc}")
            return False


class ClientRepDBAdapter(ClientRepBase):
    """Adapter: делает ClientRepDB совместимым с интерфейсом ClientRepBase."""

    def __init__(self, db_repo: ClientRepDB) -> None:
        # сохраняем "адаптируемый" объект, чтобы read_all уже мог к нему обращаться
        self.db_repo = db_repo
        # file_path фиктивный, в БД он не используется
        super().__init__(file_path=":db:")

    # Переопределение чтения и записи
    def read_all(self) -> None:
        """Загрузка всех клиентов из БД в self.items для совместимости."""
        clients = self.db_repo.get_all()
        self.items = clients[:]

    def write_all(self, file_name: Optional[str] = None) -> None:
        """Синхронизировать self.items с БД (простой вариант: очистить и залить)."""
        self.db_repo.clear_all()
        for client in self.items:
            new_id = self.db_repo.add(client)
            client.set_id(new_id)

    def _load_from_storage(self) -> List[dict]:
        return []

    def _dump_to_storage(
        self,
        data: List[dict],
        file_name: Optional[str] = None,
    ) -> None:
        return None

    # Перенаправление основных операций напрямую в ClientRepDB.
    def get_by_id(self, client_id: int) -> Optional[Client]:
        return self.db_repo.get_by_id(client_id)

    def get_k_n_short_list(self, k: int, n: int) -> List[Client]:
        return self.db_repo.get_k_n_short_list(k, n)

    def add(self, client: Client) -> int:
        self.read_all()
        if not self._is_unique(client):
            return -1
        new_id = self.db_repo.add(client)
        client.set_id(new_id)
        self.read_all()
        return new_id

    def replace_by_id(self, client_id: int, new_client: Client) -> bool:
        self.read_all()
        if not self._is_unique(new_client):
            return False
        ok = self.db_repo.replace_by_id(client_id, new_client)
        self.read_all()
        return ok

    def delete_by_id(self, client_id: int) -> bool:
        ok = self.db_repo.delete_by_id(client_id)
        self.read_all()
        return ok

    def get_count(self) -> int:
        return self.db_repo.get_count()

    def print_all(self) -> None:
        self.read_all()
        super().print_all()


class ClientRepDBDecorator:
    """
    Декоратор для ClientRepDB.

    Добавляет возможность передавать filter_fn и sort_key
    в методы get_k_n_short_list и get_count.
    """

    def __init__(self, wrapped: ClientRepDB) -> None:
        self._wrapped = wrapped

    def get_k_n_short_list(
        self,
        k: int,
        n: int,
        filter_fn: Optional[Callable[[Client], bool]] = None,
        sort_key: Optional[Callable[[Client], Any]] = None,
        reverse: bool = False,
    ) -> List[Client]:
        """
        Расширенный вариант пагинации:

        1. Берём всех клиентов из БД (get_all)
        2. Применяем filter_fn, если передан
        3. Сортируем по sort_key, если передан
        4. Возвращаем k-ю страницу по n элементов
        """
        if n <= 0 or k <= 0:
            return []

        clients = self._wrapped.get_all()

        if filter_fn is not None:
            clients = [c for c in clients if filter_fn(c)]

        if sort_key is not None:
            clients.sort(key=sort_key, reverse=reverse)

        start = (k - 1) * n
        end = start + n
        return clients[start:end]

    def get_count(
        self,
        filter_fn: Optional[Callable[[Client], bool]] = None,
    ) -> int:
        """
        Расширенный get_count с фильтром.

        - если filter_fn не задан — делегируем в ClientRepDB.get_count()
        - если задан — считаем только тех клиентов, кто прошёл фильтр
        """
        if filter_fn is None:
            return self._wrapped.get_count()

        clients = self._wrapped.get_all()
        return sum(1 for c in clients if filter_fn(c))

    def __getattr__(self, name: str) -> Any:
        """
        Все остальные методы/атрибуты делегируем обёрнутому ClientRepDB.

        Благодаря этому декоратор "выглядит" как обычный ClientRepDB
        и его можно использовать в существующем коде вместо него.
        """
        return getattr(self._wrapped, name)


class ClientRepFileDecorator:
    """
    Декоратор для репозиториев, работающих с файлами (ClientRepBase и его наследники).

    Добавляет возможность передачи filter_fn и sort_key
    в методы get_k_n_short_list и get_count.
    """

    def __init__(self, wrapped: ClientRepBase) -> None:
        self._wrapped = wrapped

    def get_k_n_short_list(
        self,
        k: int,
        n: int,
        filter_fn: Optional[Callable[[Client], bool]] = None,
        sort_key: Optional[Callable[[Client], Any]] = None,
        reverse: bool = False,
    ) -> List[Client]:
        """
        Расширенная пагинация для файлового репозитория.

        1. Обновляем items из файла (read_all)
        2. Берём список клиентов
        3. Применяем фильтр (если задан)
        4. Применяем сортировку (если задана)
        5. Возвращаем k-ю страницу по n элементов
        """
        if n <= 0 or k <= 0:
            return []

        self._wrapped.read_all()
        clients = list(self._wrapped.items)

        if filter_fn is not None:
            clients = [c for c in clients if filter_fn(c)]

        if sort_key is not None:
            clients.sort(key=sort_key, reverse=reverse)

        start = (k - 1) * n
        end = start + n
        return clients[start:end]

    def get_count(
        self,
        filter_fn: Optional[Callable[[Client], bool]] = None,
    ) -> int:
        """
        Расширенный get_count:

        - Если filter_fn не задан, просто делегируем в базовый get_count()
        - Если filter_fn задан, считаем только тех клиентов, кто ему соответствует.
        """
        self._wrapped.read_all()

        if filter_fn is None:
            return self._wrapped.get_count()

        return sum(1 for c in self._wrapped.items if filter_fn(c))

    def __getattr__(self, name: str) -> Any:
        """
        Все остальные методы/атрибуты делегируем обёрнутому репозиторию.

        Благодаря этому декоратор "выглядит" как обычный ClientRepBase
        (ClientRepJson / ClientRepYaml) и его можно использовать вместо него.
        """
        return getattr(self._wrapped, name)


POSTGRES_USER = "postgres"
POSTGRES_PASSWORD = "postgres_password"
POSTGRES_HOST = "localhost"
POSTGRES_PORT = 5432
TARGET_DB = "hair_salon"


def ensure_database_exists() -> None:
    """
    Подключаемся к postgres и убеждаемся, что база hair_salon существует.
    Если нет — создаём.
    """
    conn = psycopg2.connect(
        dbname="postgres",
        user=POSTGRES_USER,
        password=POSTGRES_PASSWORD,
        host=POSTGRES_HOST,
        port=POSTGRES_PORT,
    )
    conn.autocommit = True

    with conn.cursor() as cur:
        cur.execute("SELECT 1 FROM pg_database WHERE datname = %s", (TARGET_DB,))
        exists = cur.fetchone()

        if not exists:
            print(f"База данных '{TARGET_DB}' не существует — создаю...")
            cur.execute(sql.SQL("CREATE DATABASE {}").format(sql.Identifier(TARGET_DB)))
        else:
            print(f"База данных '{TARGET_DB}' уже существует.")

    conn.close()


def ensure_clients_table() -> None:
    """
    Создаёт таблицу clients, если её нет.
    Если таблица пустая — сразу вставляет клиента по умолчанию.
    """
    conn = psycopg2.connect(
        dbname=TARGET_DB,
        user=POSTGRES_USER,
        password=POSTGRES_PASSWORD,
        host=POSTGRES_HOST,
        port=POSTGRES_PORT,
    )
    with conn:
        with conn.cursor() as cur:
            cur.execute(
                """
                CREATE TABLE IF NOT EXISTS clients (
                    id              SERIAL PRIMARY KEY,
                    first_name      VARCHAR(100) NOT NULL,
                    last_name       VARCHAR(100) NOT NULL,
                    father_name     VARCHAR(100) NOT NULL,
                    haircut_counter INTEGER      NOT NULL,
                    discount        INTEGER      NOT NULL
                );
                """
            )

            cur.execute("SELECT COUNT(*) FROM clients;")
            count = cur.fetchone()[0]

            if count == 0:
                print("Добавляю клиента по умолчанию...")
                cur.execute(
                    """
                    INSERT INTO clients (
                        first_name, last_name, father_name,
                        haircut_counter, discount
                    )
                    VALUES (%s, %s, %s, %s, %s)
                    """,
                    ("Иван", "Иванов", "Иванович", 4, 10),
                )

    conn.close()
    print("Таблица clients готова.")


def initialize_database() -> None:
    ensure_database_exists()
    ensure_clients_table()


if __name__ == "__main__":
    # Пример: работа с файловым репозиторием через декоратор
    base_repo = ClientRepJson("clients.json")
    repo = ClientRepFileDecorator(base_repo)

    big_discount = lambda c: c.get_discount() >= 10  # noqa: E731

    print("Всего клиентов (без фильтра):", repo.get_count())
    print("Клиентов со скидкой >= 10:", repo.get_count(filter_fn=big_discount))

    page = repo.get_k_n_short_list(
        k=1,
        n=5,
        filter_fn=big_discount,
        sort_key=lambda c: c.get_last_name(),
        reverse=False,
    )

    print("Страница с фильтром и сортировкой:")
    for client in page:
        print(client)
