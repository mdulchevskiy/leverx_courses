"""
Даны 2 файла (смотрите в прикрепленных файлах):

- students.json (доступны поля id, name, birthday, room, sex)
- rooms.json (доступные поля id, name)

- Необходимо с использованием базы MySQL создать схему данных соответствующую данным файлам (связь многие к одному).

- Написать скрипт, целью которого будет загрузка этих двух файлов и запись данных в базу.

- Сделать запросы к базе данных чтобы вернуть:
    - список комнат и количество студентов в каждой из них
    - top 5 комнат, где самые маленький средний возраст студентов
    - top 5 комнат с самой большой разницей в возрасте студентов
    - список комнат где живут разнополые студенты
    (Всю "математику" делать стоит на уровне БД)

- Предложить варианты оптимизации запросов с использования индексов
    - в результате надо сгенерировать SQL запрос который добавит нужные индексы

- Выгрузить результат в формате JSON или XML

- Командный интерфейс должен поддерживать следующие входные параметры
    - students  # путь к файлу студентов
    - rooms  # путь к файлу комнат
    - format  # выходной формат (xml или json)

Ожидается использование ООП и SOLID.
Ожидается отсутсвие использования ORM (т.е. надо использовать SQL)
"""
import argparse
import sqlalchemy
from task_1 import (args_validator,
                    Reader,
                    Writer, )


# Создание пользователя в самой базе данных
"CREATE USER 'test_user'@'localhost' IDENTIFIED BY 'password';"
"GRANT ALL PRIVILEGES ON *.* TO 'test_user'@'localhost';"


USER = "test_user"
PASSWORD = "password"
SERVER = "localhost"
DATABASE = "task_4_db"


class MySQLDBClass:
    def __init__(self, user, password, server, database):
        self.user = user
        self.password = password
        self.server = server
        self.database = database
        self.__engine = sqlalchemy.create_engine(f'mysql+pymysql://{user}:{password}@{server}')

    def create_database(self):
        self.__engine.execute(f"CREATE DATABASE IF NOT EXISTS {self.database};")
        self.__engine.execute(f"USE {self.database};")

    def create_index(self, indexed_table: str, indexed_columns: list, index_name: str):
        if all((indexed_table, indexed_table, index_name)):
            find_index_query = f"""
                SELECT COUNT(*) 
                FROM (SELECT INDEX_NAME 
                      FROM INFORMATION_SCHEMA.STATISTICS 
                      WHERE table_name = '{indexed_table}' and index_name = '{index_name}') AS p;
                """
            index_exists = self.__engine.execute(find_index_query).fetchall()[0][0]
            if not index_exists:
                create_index_query = f"CREATE INDEX {index_name} ON {indexed_table}({', '.join(indexed_columns)});"
                self.__engine.execute(create_index_query)
            else:
                print(f'Index "{index_name}" already exists!')
        else:
            print('Wrong arguments!')

    def execute(self, query):
        return self.__engine.execute(query)


def dicts_to_str(dict_list: list) -> str:
    tuple_list = [f'{tuple(dictionary.values())}' for dictionary in dict_list]
    string = ', '.join(tuple_list)
    return string


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('-rfr', '--rooms_file_root', required=True)
    parser.add_argument('-sfr', '--students_file_root', required=True)
    parser.add_argument('-of', '--output_format', required=True)
    args = parser.parse_args()

    if args_validator(args):
        rooms_str = dicts_to_str(Reader.read_json(args.rooms_file_root))
        students_str = dicts_to_str(Reader.read_json(args.students_file_root))

        msql_db = MySQLDBClass(USER, PASSWORD, SERVER, DATABASE)
        msql_db.create_database()

        create_and_upload_queries = [
            """
            CREATE TABLE IF NOT EXISTS rooms(
                id INT NOT NULL,
                name VARCHAR(40) NOT NULL,
                PRIMARY KEY (id)
            );
            """,
            """
            CREATE TABLE IF NOT EXISTS students(
                id INT NOT NULL,
                name VARCHAR(40) NOT NULL,
                birthday DATETIME NOT NULL,
                sex VARCHAR(1) NOT NULL,
                room_id INT,
                PRIMARY KEY (id),
                FOREIGN KEY (room_id) REFERENCES rooms (id)
            )
            """,
            f"""
                INSERT IGNORE rooms(id, name) 
                VALUES {rooms_str};
                """,
            f"""
                INSERT IGNORE students(birthday, id, name, room_id, sex) 
                VALUES {students_str};
                """
        ]
        for query in create_and_upload_queries:
            msql_db.execute(query)

        # Практически в два раза ускоряет запросы query_2 и query_3: в среднем для 1000 запросов прирост скорости
        # 0,023 с. -> 0,012 с. и 0,024 с. -> 0,014 с. соответственно.
        msql_db.create_index('students', ['room_id', 'birthday'], 'room_id_birthday')

        select_queries = [
            """
            SELECT room_id, count(id) as "students_amount"
            FROM students
            GROUP BY room_id;
            """,
            """
            SELECT t.room_id
            FROM (SELECT room_id, birthday, DATEDIFF(CURRENT_DATE, birthday) as "age"
                  FROM students) AS t
            GROUP BY room_id
            ORDER BY AVG(t.age)
            LIMIT 5;
            """,
            """
            SELECT t.room_id
            FROM (SELECT room_id, birthday, DATEDIFF(CURRENT_DATE, birthday) as "age"
                  FROM students) AS t
            GROUP BY room_id
            ORDER BY max(t.age) - min(t.age) DESC
            LIMIT 5;
            """,
            """
            SELECT t.room_id
            FROM (SELECT room_id, count(id) as "students_amount", count(case when sex = "M" then 1 end) as "male_amount"
                  FROM students
                  GROUP BY room_id) as t
            WHERE t.students_amount != t.male_amount;
            """
        ]
        query_1 = msql_db.execute(select_queries[0]).fetchall()
        query_2_4 = [msql_db.execute(query).fetchall() for query in select_queries[1:]]

        result_dict_for_query_1 = {
            'query_1': [{'id': room[0], 'students_amount': room[1]} for room in query_1]
        }
        result_dict_for_query_2_4 = {
            f'query_{i + 2}': [room[0] for room in result] for i, result in enumerate(query_2_4)
        }
        result_dict_for_query_1.update(result_dict_for_query_2_4)

        Writer.write_to_file(result_dict_for_query_1, args.output_format)


if __name__ == '__main__':
    main()
