class Client:
    def __init__(self, first_name, last_name, father_name, haircut_counter, discount):
        # Валидация всех полей перед созданием объекта
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

    # Статические методы валидации
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

    # Метод для вывода
    def __str__(self):
        return (f"Client: {self.__last_name} {self.__first_name} {self.__father_name}, "
                f"стрижек: {self.__haircut_counter}, скидка: {self.__discount}%")
