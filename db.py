import sqlite3
from datetime import datetime


class DataBase:
    def __init__(self):
        # Установка соединения с базой данных или создание файла базы данных, если он не существует
        conn = sqlite3.connect('example.db')
        # Создание курсора для выполнения SQL-запросов
        cursor = conn.cursor()
        # Создание таблицы
        cursor.execute('''CREATE TABLE IF NOT EXISTS user_data (
                            user_id INTEGER PRIMARY KEY,
                            count_free_translate INTEGER,
                            have_subscription BOOLEAN,
                            date_due DATE
                        )''')
        
        cursor.execute('''CREATE TABLE IF NOT EXISTS user_language (
                            user_id INTEGER PRIMARY KEY,
                            language VARCHAR(100)
                        )''')
        # Сохранение изменений и закрытие соединения
        conn.commit()
        conn.close()

    def add_user(self, user_id, count_free_translate, have_subscription, date_due):
        try:
            # Установка соединения с базой данных или создание файла базы данных, если он не существует
            conn = sqlite3.connect('example.db')
            # Создание курсора для выполнения SQL-запросов
            cursor = conn.cursor()
            # Вставка новой записи
            cursor.execute('''INSERT INTO user_data (user_id, count_free_translate, have_subscription, date_due)
                              VALUES (?, ?, ?, ?)''', (user_id, count_free_translate, have_subscription, date_due))
            cursor.execute('''INSERT INTO user_language (user_id, language)
                    VALUES (?, ?)''', (user_id, None))
            # Сохранение изменений и закрытие соединения
            conn.commit()
            conn.close()
            print("Запись успешно добавлена.")
        except sqlite3.Error as e:
            print("Ошибка при добавлении записи в базу данных:", e)

    def check_user_existence(self, user_id) -> bool:
        try:
            # Установка соединения с базой данных
            conn = sqlite3.connect('example.db')
            # Создание курсора для выполнения SQL-запросов
            cursor = conn.cursor()
            # Поиск пользователя по user_id
            cursor.execute("SELECT * FROM user_data WHERE user_id=?", (user_id,))
            user = cursor.fetchone()
            # Проверка наличия пользователя
            if user:
                print("Пользователь с user_id =", user_id, "найден.")
                return True
            else:
                print("Пользователь с user_id =", user_id, "не найден.")
                return False
        except sqlite3.Error as e:
            print("Ошибка при выполнении запроса:", e)
            return False
        finally:
            # Закрытие соединения
            conn.close()

    def get_count_free_translate(self, user_id) -> int:
        try:
            # Установка соединения с базой данных
            conn = sqlite3.connect('example.db')
            # Создание курсора для выполнения SQL-запросов
            cursor = conn.cursor()
            # Получение текущего значения count_free_translate для указанного пользователя
            cursor.execute("SELECT count_free_translate FROM user_data WHERE user_id=?", (user_id,))
            current_count = cursor.fetchone()[0]
            # Вывод текущего значения
            print("Текущее значение count_free_translate для пользователя с user_id =", user_id, ":", current_count)
            # Возвращаем текущее значение
            return current_count
        except sqlite3.Error as e:
            print("Ошибка при выполнении запроса:", e)
            return None
        finally:
            # Закрытие соединения
            conn.close()

    def update_count_free_translate(self, user_id, new_count):
        try:
            # Установка соединения с базой данных
            conn = sqlite3.connect('example.db')
            # Создание курсора для выполнения SQL-запросов
            cursor = conn.cursor()
            # Обновление значения count_free_translate для указанного пользователя
            cursor.execute("UPDATE user_data SET count_free_translate=? WHERE user_id=?", (new_count, user_id))
            # Подтверждение изменений
            conn.commit()
            print("Значение count_free_translate успешно изменено для пользователя с user_id =", user_id)
        except sqlite3.Error as e:
            print("Ошибка при выполнении запроса:", e)
        finally:
            # Закрытие соединения
            conn.close()

    def get_have_subscription(self, user_id) -> bool:
        try:
            # Установка соединения с базой данных
            conn = sqlite3.connect('example.db')
            # Создание курсора для выполнения SQL-запросов
            cursor = conn.cursor()
            # Получение текущего значения have_subscription для указанного пользователя
            cursor.execute("SELECT have_subscription FROM user_data WHERE user_id=?", (user_id,))
            # print(type(cursor.fetchone()[0]))
            current_subscription = bool(cursor.fetchone()[0])
            # Вывод текущего значения
            print("Текущее значение have_subscription для пользователя с user_id =", user_id, ":", current_subscription)
            # Возвращаем текущее значение
            return bool(current_subscription)
        except sqlite3.Error as e:
            print("Ошибка при выполнении запроса:", e)
            return None
        finally:
            # Закрытие соединения
            conn.close()

    def update_have_subscription(self, user_id, new_subscription):
        try:
            # Установка соединения с базой данных
            conn = sqlite3.connect('example.db')
            # Создание курсора для выполнения SQL-запросов
            cursor = conn.cursor()
            # Обновление значения have_subscription для указанного пользователя
            cursor.execute("UPDATE user_data SET have_subscription=? WHERE user_id=?", (new_subscription, user_id))
            # Подтверждение изменений
            conn.commit()
            print("Значение have_subscription успешно изменено для пользователя с user_id =", user_id)
        except sqlite3.Error as e:
            print("Ошибка при выполнении запроса:", e)
        finally:
            # Закрытие соединения
            conn.close()

    def get_date_due(self, user_id) -> str:
        try:
            # Установка соединения с базой данных
            conn = sqlite3.connect('example.db')
            # Создание курсора для выполнения SQL-запросов
            cursor = conn.cursor()
            # Получение текущего значения date_due для указанного пользователя
            cursor.execute("SELECT date_due FROM user_data WHERE user_id=?", (user_id,))
            current_date_due = cursor.fetchone()[0]
            # Вывод текущего значения
            print("Текущее значение date_due для пользователя с user_id =", user_id, ":", current_date_due)
            # Возвращаем текущее значение
            return current_date_due
        except sqlite3.Error as e:
            print("Ошибка при выполнении запроса:", e)
            return None
        finally:
            # Закрытие соединения
            conn.close()

    def update_date_due(self, user_id, new_date_due):
        try:
            # Установка соединения с базой данных
            conn = sqlite3.connect('example.db')
            # Создание курсора для выполнения SQL-запросов
            cursor = conn.cursor()
            # Обновление значения date_due для указанного пользователя
            cursor.execute("UPDATE user_data SET date_due=? WHERE user_id=?", (new_date_due, user_id))
            # Подтверждение изменений
            conn.commit()
            print("Значение date_due успешно изменено для пользователя с user_id =", user_id)
        except sqlite3.Error as e:
            print("Ошибка при выполнении запроса:", e)
        finally:
            # Закрытие соединения
            conn.close()

    def print_all_data(self):
        try:
            # Установка соединения с базой данных
            conn = sqlite3.connect('example.db')
            # Создание курсора для выполнения SQL-запросов
            cursor = conn.cursor()
            # Выбор всех данных из таблицы
            cursor.execute("SELECT * FROM user_data")
            # Получение результатов запроса
            rows = cursor.fetchall()
            # Вывод результатов
            for row in rows:
                print(row)
        except sqlite3.Error as e:
            print("Ошибка при выполнении запроса:", e)
        finally:
            # Закрытие соединения
            conn.close()
    
    def update_language(self, user_id, language):
        try:
            # Установка соединения с базой данных
            conn = sqlite3.connect('example.db')
            # Создание курсора для выполнения SQL-запросов
            cursor = conn.cursor()
            # Обновление значения date_due для указанного пользователя
            cursor.execute("UPDATE user_language SET language=? WHERE user_id=?", (language, user_id))
            # Подтверждение изменений
            conn.commit()
        except sqlite3.Error as e:
            print("Ошибка при выполнении запроса:", e)
        finally:
            # Закрытие соединения
            conn.close()

    def get_language(self, user_id):
        try:
            # Установка соединения с базой данных
            conn = sqlite3.connect('example.db')
            # Создание курсора для выполнения SQL-запросов
            cursor = conn.cursor()
            # Выбор всех данных из таблицы
            cursor.execute("SELECT language FROM user_language WHERE user_id=?", (user_id,))
            # Получение результатов запроса
            rows = cursor.fetchall()
            # Вывод результатов
            return rows[0][0]
        except sqlite3.Error as e:
            print("Ошибка при выполнении запроса:", e)
            return None
        finally:
            # Закрытие соединения
            conn.close()