
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
