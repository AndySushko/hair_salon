import json
from typing import Dict, Any


class Client:
    def __init__(self, *args, **kwargs):
        if len(args) == 1:
            # Один аргумент - может быть словарем или JSON строкой
            if isinstance(args[0], str):
                # JSON строка
                try:
                    data = json.loads(args[0])
                    self.__init_from_dict(data)
                except json.JSONDecodeError:
                    raise ValueError("Некорректный JSON формат")
            elif isinstance(args[0], dict):
                # Словарь
                self.__init_from_dict(args[0])
            else:
                raise ValueError("Не поддерживаемый тип аргумента")
        elif len(args) == 5:
            # Обычное создание с 5 позиционными аргументами
            self.__validate_and_init(args[0], args[1], args[2], args[3], args[4])
        elif kwargs:
            # Создание из именованных параметров
            self.__init_from_kwargs(kwargs)
        else:
            raise ValueError("Неверное количество аргументов")

    def __init_from_dict(self, data: Dict[str, Any]):
        """Инициализация из словаря"""
        required_fields = ['first_name', 'last_name', 'father_name', 'haircut_counter', 'discount']
        missing_fields = [field for field in required_fields if field not in data]
        if missing_fields:
            raise ValueError(f"Отсутствуют обязательные поля: {missing_fields}")

        self.__validate_and_init(
            data['first_name'],
            data['last_name'],
            data['father_name'],
            data['haircut_counter'],
            data['discount']
        )

    def __init_from_kwargs(self, kwargs: Dict[str, Any]):
        """Инициализация из именованных параметров"""
        required_fields = ['first_name', 'last_name', 'father_name', 'haircut_counter', 'discount']
        missing_fields = [field for field in required_fields if field not in kwargs]
        if missing_fields:
            raise ValueError(f"Отсутствуют обязательные поля: {missing_fields}")

        self.__validate_and_init(
            kwargs['first_name'],
            kwargs['last_name'],
            kwargs['father_name'],
            kwargs['haircut_counter'],
            kwargs['discount']
        )

    def __validate_and_init(self, first_name, last_name, father_name, haircut_counter, discount):
        """Общая валидация и инициализация полей"""
        self.__validate_name(first_name, "first_name")
        self.__validate_name(last_name, "last_name")
        self.__validate_name(father_name, "father_name")
        self.__validate_haircut_counter(haircut_counter)
        self.__validate_discount(discount)

        self.__first_name = first_name
        self.__last_name = last_name
        self.__father_name = father_name
        self.__haircut_counter = haircut_counter
        self.__discount = discount

    # Статические методы валидации (остаются без изменений)
    @staticmethod
    def __validate_name(name, field_name):
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
    def __validate_haircut_counter(haircut_counter):
        """Валидация количества стрижек"""
        if not isinstance(haircut_counter, int):
            raise ValueError("haircut_counter должен быть целым числом")
        if haircut_counter < 0:
            raise ValueError("haircut_counter не может быть отрицательным")

    @staticmethod
    def __validate_discount(discount):
        """Валидация скидки"""
        if not isinstance(discount, (int, float)):
            raise ValueError("discount должен быть числом")
        if discount < 0 or discount > 100:
            raise ValueError("discount должен быть в диапазоне от 0 до 100")

    # Геттеры
    def get_first_name(self):
        return self.__first_name

    def get_last_name(self):
        return self.__last_name

    def get_father_name(self):
        return self.__father_name

    def get_haircut_counter(self):
        return self.__haircut_counter

    def get_discount(self):
        return self.__discount

    # Сеттеры с валидацией
    def set_first_name(self, first_name):
        self.__validate_name(first_name, "first_name")
        self.__first_name = first_name

    def set_last_name(self, last_name):
        self.__validate_name(last_name, "last_name")
        self.__last_name = last_name

    def set_father_name(self, father_name):
        self.__validate_name(father_name, "father_name")
        self.__father_name = father_name

    def set_haircut_counter(self, haircut_counter):
        self.__validate_haircut_counter(haircut_counter)
        self.__haircut_counter = haircut_counter

    def set_discount(self, discount):
        self.__validate_discount(discount)
        self.__discount = discount

    # Метод для полной записи объекта
    def display_full(self):
        """Вывод полной версии объекта"""
        print("=" * 50)
        print("ПОЛНАЯ ИНФОРМАЦИЯ О КЛИЕНТЕ")
        print("=" * 50)
        print(f"Фамилия:         {self.__last_name}")
        print(f"Имя:             {self.__first_name}")
        print(f"Отчество:        {self.__father_name}")
        print(f"Количество стрижек: {self.__haircut_counter}")
        print(f"Скидка:          {self.__discount}%")
        print("=" * 50)

    # Метод для представления объекта (краткая запись)
    def __str__(self):
        return (f"Клиент: {self.__last_name} {self.__first_name[0]}.{self.__father_name[0]}., "
              f"стрижек: {self.__haircut_counter}, скидка: {self.__discount}%")

    # Методы сравнения объектов
    def __eq__(self, other):
        """Сравнение на равенство (==)"""
        if not isinstance(other, Client):
            return False

        return (self.__first_name == other.__first_name and
                self.__last_name == other.__last_name and
                self.__father_name == other.__father_name and
                self.__haircut_counter == other.__haircut_counter and
                self.__discount == other.__discount)

    def __ne__(self, other):
        """Сравнение на неравенство (!=)"""
        return not self.__eq__(other)

