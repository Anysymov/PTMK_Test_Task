import psycopg2
from datetime import datetime
from random import randint, randrange
from sys import argv
from time import time

start_time = time() # Начало замера времени для параметра 4

if len(argv) > 1: # Получение входных данных
    if str(argv[1]) == "2":
        try:
            input_data = str(argv[1]) + " " + str(argv[2]) + " " + str(argv[3]) + " " + str(argv[4])
        except:
            print("2 takes more arguments")
    else:
        input_data = str(argv[1])
else:
    print("Wrong input")

class Human(): # Базовый класс для формирования данных о струднике
    def __init__(self, name, gender, birthday=None):
        self.gender = gender
        self.name = name

        if birthday != None:
            if type(birthday) == str:
                self.birthday = datetime.strptime(birthday, "%Y-%m-%d").date()
            else:
                self.birthday = birthday
        else:
            year = randint(1960, 2005)
            month = randint(1, 12)
            date = randint(1, 28)
            self.birthday = datetime.strptime(f"{year}-{month}-{date}", "%Y-%m-%d").date()
        
        self.age = (datetime.today().date() - self.birthday).days // 365


class Employee(Human): # Берёт данные из родительского класса и отправляет их в базу данных или же принимает пакет данных и отправляет его

    def add_employee_to_db(self, multiple=None):
        conn = psycopg2.connect(dbname="postgres", user="postgres", password="123456", host="127.0.0.1", port="5432")
        conn.autocommit = True
        cursor = conn.cursor()

        if multiple == None:
            values = f"""({"'" + self.name + "'"}, {"'" + str(self.birthday) + "'"}, {"'" + self.gender + "'"})"""
        else:
            values = ""

            first = True

            for human in multiple:
                value = f"""({"'" + human.name + "'"}, {"'" + str(human.birthday) + "'"}, {"'" + human.gender + "'"})"""

                if first == True:
                    values = values + value
                    first = False
                else:
                    values = values + ",\n" + str(value)

        sql_query = f"""INSERT INTO EmployeeData (EmployeeName, Birthday, Gender)
                        VALUES {values}"""
        
        cursor.execute(sql_query)
        conn.close()


def choose_option(option): # Выбор дальнейшего исполнения в зависимости от параметра ввода
    if option[0] == "1":
        table_creation()
    elif option[0] == "2":
        option_as_list = [option[2:]] # Убирает число и пробел из входного параметра
        users_creation(option_as_list)
    elif option[0] == "3":
        get_uniquie_users()
    elif option[0] == "4":
        employees_amount = 10000000 # Определяет количество генерируемых пользователей
        english_alpahbet = "ABCDEFGIKLMNOPRSTUVYZ" # Определяет буквы алфавита, по котороым будет проходить генерация имён. Не у всех букв есть имена (брались русскоязычные имена)

        employees_autofill(employees_amount, english_alpahbet)

        employees_autofill(100, "F", "Male") # Автоматическое заполнение 100 строк фамилией с буквы F
    elif option[0] == "5":
        employee_selection('Male', 'F')
        print(f"Process finished in {str(time() - start_time)[:6]} seconds") # Выводит время выполнения параметра 5
    else:
        pass


def table_creation(): # Параметр 1 - создание таблицы
    conn = psycopg2.connect(dbname="postgres", user="postgres", password="123456", host="127.0.0.1", port="5432")
    conn.autocommit = True
    cursor = conn.cursor()

    cursor.execute("SELECT EXISTS(SELECT * FROM pg_tables WHERE schemaname = 'public' and tablename='EmployeeData')")
    exists = cursor.fetchone()

    if not exists[0]:

        sql_query = """CREATE TABLE EmployeeData (
                                                    EmployeeName VARCHAR(100),
                                                    Birthday DATE,
                                                    Gender VARCHAR(6)
                                                    )"""
        cursor.execute(sql_query)

    conn.close()


def users_creation(data): # Параметр 2 - создание человека из полученных данных
    for i in data:
        employee_data_list = i.split()
        employee_name = employee_data_list[0]+ " " + employee_data_list[1] + " " + employee_data_list[2]

        new_employee = Employee(name=employee_name, birthday=employee_data_list[3], gender=employee_data_list[4])
        new_employee.add_employee_to_db()


def get_uniquie_users(): # Параметр 3 - получение уникальных пользователей из ранее созданной таблицы
    conn = psycopg2.connect(dbname="postgres", user="postgres", password="123456", host="127.0.0.1", port="5432")
    conn.autocommit = True
    cursor = conn.cursor()

    sql_query = """SELECT DISTINCT ON (EmployeeName, Birthday) EmployeeName, Birthday, Gender FROM EmployeeData
                    ORDER BY EmployeeName"""

    cursor.execute(sql_query)

    result = cursor.fetchall()
    unique_users_list = []

    for employee in result: # Создаётся человек, чтобы методом класса автоматически считался возраст
        new_employee = Human(name=employee[0], birthday=employee[1], gender=employee[2])
        new_line = f"{new_employee.name} {new_employee.birthday} {new_employee.gender} {new_employee.age}"
        unique_users_list.append(new_line)

    for i in unique_users_list:
        print(i)

    conn.close()


def get_list_of_names(): # Функция для получения содержимого всех файлов имён (для генерации ФИО с меньшей задержкой)
    paths_list = ["text-files/male_names.txt",
                    "text-files/male_surnames.txt",
                    "text-files/male_patronims.txt",
                    "text-files/female_names.txt",
                    "text-files/female_surnames.txt",
                    "text-files/female_patronims.txt"]

    for i in paths_list: # Обрабатывается каждый текстовый файл
        with open(i, "r") as reader:
            current_list = []

            for line in reader:
                current_list.append(line.strip())
            
            if i == "text-files/male_names.txt":
                m_names = current_list
            elif i == "text-files/male_surnames.txt":
                m_snames = current_list
            elif i == "text-files/male_patronims.txt":
                m_patr = current_list
            elif i == "text-files/female_names.txt":
                f_names = current_list
            elif i == "text-files/female_surnames.txt":
                f_snames = current_list
            elif i == "text-files/female_patronims.txt":
                f_patr = current_list
    
    return [m_names, m_patr, m_snames, f_names, f_patr, f_snames]


def employees_autofill(amount, letters, gender_preference=None): # Параметр 4 - автоматическое создание N записей с равномерным распределением первой буквы ФИО

    listof_names_lists = get_list_of_names()
    list_of_employees= []
    
    for i in range(amount):

        letter = letters[randrange(0, len(letters))]

        if gender_preference == None: # Бросок монеты определеяющий пол
            coin_toss = randint(0, 1)
        else:
            if gender_preference == "Male":
                coin_toss = 1
            else:
                coin_toss = 0

        if coin_toss == 1:
            gender = "Male"
            chosen_lists = [listof_names_lists[0], listof_names_lists[1], listof_names_lists[2]]
        else:
            gender = "Female"
            chosen_lists = [listof_names_lists[3], listof_names_lists[4], listof_names_lists[5]]

        list_with_letter = []

        for line in chosen_lists[0]:
            if line[0] == letter:
                list_with_letter.append(line)

        num1 = randrange(0, len(list_with_letter))
        num2 = randrange(0, len(chosen_lists[1]))
        num3 = randrange(0, len(chosen_lists[2]))
        
        name = list_with_letter[num1] + " " + chosen_lists[1][num2] + " " + chosen_lists[2][num3]  # Генерация ФИО
        
        new_human = Human(name=name, gender=gender)

        list_of_employees.append(new_human)

        if i % 5000 == 0 and i != 0 and i != amount: # Пакетная отправка - 5000 сотрудников за раз показывал лучший результат из различных размеров пакета по времени исполнения
            Employee.add_employee_to_db(new_human, multiple=list_of_employees)
            list_of_employees = []
        
    Employee.add_employee_to_db(new_human, multiple=list_of_employees)  # Отправка последних сотрудников, не попавших в финальный пакет


def employee_selection(gender, letter): # Параметр 5 - выбор сотрудников по первой букве и полу
    
    conn = psycopg2.connect(dbname="postgres", user="postgres", password="123456", host="127.0.0.1", port="5432")
    conn.autocommit = True
    cursor = conn.cursor()

    sql_query = f"""SELECT * FROM EmployeeData WHERE Gender='{gender}' AND EmployeeName LIKE '{letter}%'"""
    cursor.execute(sql_query)

    result = cursor.fetchall()

    results_list = []

    for employee in result: # Сначала создаётся список
        results_list.append(f"{employee[2]}, {employee[0]}, {employee[1]}")
    
    for i in results_list: # затем список печатается
        print(i)

    conn.close()


choose_option(input_data) # Запускается выбор действия в зависимости от параметра на входе
