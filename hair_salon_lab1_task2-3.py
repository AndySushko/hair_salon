# Задание 2-3
class Client:
    def __init__(self, first_name, last_name, father_name, haircut_counter, discount):
        self.__first_name = first_name
        self.__last_name = last_name
        self.__father_name = father_name
        self.__haircut_counter = haircut_counter
        self.__discount = discount

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

    # Сеттеры
    def set_first_name(self, first_name):
        self.__father_name = first_name

    def set_last_name(self, last_name):
        self.__father_name = last_name

    def set_father_name(self, father_name):
        self.__father_name = father_name

    def set_haircut_counter(self, haircut_counter):
        if haircut_counter >= 0:  # проверка, что кол-во стрижек неотрицательно
            self.__haircut_counter = haircut_counter

    def set_discount(self, discount):
        if discount >= 0 and discount <= 100:   # проверка, что размер скидки в диапазоне 0-100%
            self.__discount = discount