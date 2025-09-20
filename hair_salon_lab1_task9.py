import json
from typing import Dict, Any

class ClientShort:
    """Базовый класс с краткой информацией о клиенте"""
    def __init__(self, last_name: str, first_name: str, father_name: str, haircut_counter: int):

        self._validate_name(last_name, "last_name")
        self._validate_name(first_name, "first_name")
        self._validate_name(father_name, "father_name")
        self._validate_haircut_counter(haircut_counter)

        self.__last_name = last_name
        self.__first_name = first_name
        self.__father_name = father_name
        self.__haircut_counter = haircut_counter

    # Статические методы валидации
    @staticmethod
    def _validate_name(name, field_name):
        """Валидация имени, фамилии и отчества"""
        if not isinstance(name, str):
            raise ValueError(f"{field_name} должен быть строкой")
        if not name.strip():
            raise ValueError(f"{field_name} не может быть пустым")
        if len(name.strip()) < 2:
            raise ValueError(f"{field_name} должен содержать минимум 2 символа")
        if not name.replace(" ", "").isalpha():
            raise ValueError(f"{field_name} должен содержать только буквы и пробелы")

    @staticmethod
    def _validate_haircut_counter(haircut_counter):
        """Валидация количества стрижек"""
        if not isinstance(haircut_counter, int):
            raise ValueError("haircut_counter должен быть целым числом")
        if haircut_counter < 0:
            raise ValueError("haircut_counter не может быть отрицательным")

    # Геттеры
    def get_last_name(self) -> str:
        return self.__last_name

    def get_first_name(self) -> str:
        return self.__first_name

    def get_father_name(self) -> str:
        return self.__father_name

    def get_haircut_counter(self) -> int:
        return self.__haircut_counter

    def to_string(self) -> str:
        """Возвращает в формате 'Фамилия И.О., 1'"""
        return f"{self.__last_name.title()} {self.__first_name[0].upper()}.{self.__father_name[0].upper()}., {self.__haircut_counter}"

    # Строковые представления
    def __str__(self) -> str:
        return self.to_string()

    def __repr__(self) -> str:
        return (f"ClientShort(last_name='{self.__last_name}', first_name='{self.__first_name}', "
                f"father_name='{self.__father_name}', haircut_counter={self.__haircut_counter})")

    # Методы сравнения
    def __eq__(self, other) -> bool:
        if not isinstance(other, ClientShort):
            return False
        return (self.__last_name == other.__last_name and
                self.__first_name == other.__first_name and
                self.__father_name == other.__father_name and
                self.__haircut_counter == other.__haircut_counter)


class Client(ClientShort):
    """Класс клиента с полной информацией, наследует от ClientShort"""

    def __init__(self, *args, **kwargs):

        if len(args) == 1:
            # Обработка единичного аргумента
            data = self._parse_single_arg(args[0])
            self._init_from_data(data)
        elif len(args) == 5:
            # Обычное создание
            self._init_from_data({
                'first_name': args[0],
                'last_name': args[1],
                'father_name': args[2],
                'haircut_counter': args[3],
                'discount': args[4]
            })
        elif kwargs:
            # Создание из именованных параметров
            self._init_from_data(kwargs)
        else:
            raise ValueError("Неверное количество аргументов")

    def _parse_single_arg(self, arg):
        """Обработка единичного аргумента"""
        if isinstance(arg, str):
            try:
                return json.loads(arg)
            except json.JSONDecodeError:
                raise ValueError("Некорректный JSON формат")
        elif isinstance(arg, dict):
            return arg
        else:
            raise ValueError("Не поддерживаемый тип аргумента")

    def _init_from_data(self, data: Dict[str, Any]):
        """Инициализация из данных"""
        # Проверка обязательных полей
        required_fields = ['first_name', 'last_name', 'father_name', 'haircut_counter', 'discount']
        missing_fields = [field for field in required_fields if field not in data]
        if missing_fields:
            raise ValueError(f"Отсутствуют обязательные поля: {missing_fields}")

        # Валидация скидки
        self._validate_discount(data['discount'])

        # Вызов конструктора родительского класса
        super().__init__(
            data['last_name'],
            data['first_name'],
            data['father_name'],
            data['haircut_counter']
        )

        self.__discount = data['discount']

    @staticmethod
    def _validate_discount(discount):
        """Валидация скидки"""
        if not isinstance(discount, (int, float)):
            raise ValueError("discount должен быть числом")
        if discount < 0 or discount > 100:
            raise ValueError("discount должен быть в диапазоне от 0 до 100")

    # Геттеры
    def get_discount(self) -> int:
        return self.__discount

    # Сеттеры
    def set_discount(self, discount):
        self._validate_discount(discount)
        self.__discount = discount

    # Методы преобразования
    def to_string(self) -> str:
        """Возвращает строку в формате: 'Годящев Д.М., 5, 0'"""
        base_string = super().to_string()
        return f"{base_string}, {self.__discount}"


    def to_short_version(self) -> ClientShort:
        """Создает краткую версию клиента (без скидки)"""
        return ClientShort(
            self.get_last_name(),
            self.get_first_name(),
            self.get_father_name(),
            self.get_haircut_counter()
        )

    # Строковые представления
    def __str__(self) -> str:
        return self.to_string()

    def __repr__(self) -> str:
        return (f"Client(last_name='{self.get_last_name()}', first_name='{self.get_first_name()}', "
                f"father_name='{self.get_father_name()}', haircut_counter={self.get_haircut_counter()}, "
                f"discount={self.__discount})")

    # Методы сравнения
    def __eq__(self, other) -> bool:
        if not isinstance(other, Client):
            return False
        return (super().__eq__(other) and self.__discount == other.__discount)

    # Статические фабричные методы
    @classmethod
    def from_json(cls, json_str: str) -> 'Client':
        """Создание клиента из JSON строки"""
        return cls(json_str)

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'Client':
        """Создание клиента из словаря"""
        return cls(data)
