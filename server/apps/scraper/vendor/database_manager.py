import pymysql.cursors


class DatabaseManager(object):
    connection = None

    def __init__(self, host: str, port: int, user: str, password: str, database: str):
        self.host = host
        self.user = user
        self.port = port
        self.password = password
        self.database = database

    def connect(self):
        try:
            self.connection = pymysql.connect(
                host=self.host,
                port=self.port,
                user=self.user,
                password=self.password,
                database=self.database,
                cursorclass=pymysql.cursors.DictCursor)
            print(f"Успешное подключение к базе данных")
        except Exception as ex:
            print(f"Не удалось подключиться к базе данных: {ex}")
            exit()
            # raise ex

    def close(self):
        self.connection.close()

    def prepare_database(self):
        with self.connection.cursor() as cursor:
            cursor.execute("SET SQL_BIG_SELECTS = 'ON';")
            cursor.execute("SET MAX_JOIN_SIZE = 18446744073709551615;")
            # cursor.execute("SET SQL_BIG_SELECTS = 'OFF';")
            # cursor.execute("SET MAX_JOIN_SIZE = 18446744;")
            print("Подготовка базы данных завершена")
            pass

    def prepare_tables(self):
        with self.connection.cursor() as cursor:
            try:
                cursor.execute(f"""
                    CREATE TABLE IF NOT EXISTS ReportArchive (
                        report_id INT AUTO_INCREMENT PRIMARY KEY,
                        report_content MEDIUMTEXT NOT NULL,
                        report_json JSON NOT NULL,
                        report_date DATE NOT NULL
                    );""")
                print("Приведена таблица ReportArchive")

                cursor.execute(f"""
                    CREATE TABLE IF NOT EXISTS StudentArchive (
                        record_id INT AUTO_INCREMENT PRIMARY KEY,
                        institute_name VARCHAR(255) NOT NULL,
                        course_name VARCHAR(16) NOT NULL,
                        group_name VARCHAR(16) NOT NULL,
                        student_name VARCHAR(255) NOT NULL,
                        student_id INT NOT NULL,
                        record_date DATE NOT NULL
                    );""")
                print("Приведена таблица StudentArchive")

                cursor.execute("DROP TABLE IF EXISTS Students_tmp, StudentGroups_tmp, Institutes_tmp, Courses_tmp;")
                print("tmp таблицы очищены")

                cursor.execute(f"""
                    CREATE TABLE IF NOT EXISTS Institutes (
                    institute_id INT UNIQUE PRIMARY KEY,
                    institute_name VARCHAR(255) NOT NULL,
                    institute_num INT NOT NULL);""")
                print("Приведена таблица Institutes")

                cursor.execute(f"""
                    CREATE TABLE IF NOT EXISTS Courses (
                    course_id INT UNIQUE PRIMARY KEY,
                    course_name VARCHAR(16) NOT NULL);""")
                print("Приведена таблица Courses")

                cursor.execute(f"""
                    CREATE TABLE IF NOT EXISTS StudentGroups (
                    group_id INT UNIQUE,
                    group_name VARCHAR(16) NOT NULL,
                    institute INT NOT NULL,
                    course INT NOT NULL,
                    PRIMARY KEY (group_id),
                    FOREIGN KEY (institute) REFERENCES Institutes (institute_id) ON DELETE CASCADE,
                    FOREIGN KEY (course) REFERENCES Courses (course_id) ON DELETE CASCADE);""")
                print("Приведена таблица StudentGroups")

                cursor.execute(f"""
                    CREATE TABLE IF NOT EXISTS Students (
                    student_id INT UNIQUE,
                    student_name VARCHAR(255) NOT NULL,
                    student_group INT NOT NULL,
                    leader BOOLEAN NOT NULL,
                    PRIMARY KEY (student_id),
                    FOREIGN KEY (student_group) REFERENCES StudentGroups (group_id) ON DELETE CASCADE);""")
                print("Приведена таблица Students")

                cursor.execute(f"""CREATE TABLE IF NOT EXISTS Institutes_tmp
                        SELECT * FROM Institutes;""")
                print("Приведена таблица Institutes_tmp")

                cursor.execute(f"""CREATE TABLE IF NOT EXISTS Courses_tmp
                        SELECT * FROM Courses;""")
                print("Приведена таблица Courses_tmp")

                cursor.execute(f"""CREATE TABLE IF NOT EXISTS StudentGroups_tmp
                        SELECT * FROM StudentGroups;""")
                print("Приведена таблица StudentGroups_tmp")

                cursor.execute(f"""CREATE TABLE IF NOT EXISTS Students_tmp
                        SELECT * FROM Students;""")
                print("Приведена таблица Students_tmp")

                cursor.execute("DELETE FROM Institutes;")
                cursor.execute("DELETE FROM Courses;")
                cursor.execute("DELETE FROM StudentGroups;")
                cursor.execute("DELETE FROM Students;")
                print("Копирование в tmp таблицы завершено, основные таблицы очищены")

                # отправляем изменения, так как ошибок не возникло
                self.connection.commit()
                print("Подготовка таблиц прошла успешно")
            except Exception as ex:
                print(f"Не удалось завершить подготовку таблиц: {ex}")
                return "exception"
                # raise ex

    def rollback_tables(self):
        with self.connection.cursor() as cursor:  # удаляем по порядку, согласно схеме
            cursor.execute("DROP TABLE IF EXISTS Students, StudentGroups, Institutes, Courses;")
            print("Основные таблицы удалены")

            cursor.execute(f"""CREATE TABLE IF NOT EXISTS Institutes
                                    SELECT * FROM Institutes_tmp;""")
            print("Откат таблицы Institutes")

            cursor.execute(f"""CREATE TABLE IF NOT EXISTS Courses
                                    SELECT * FROM Courses_tmp;""")
            print("Откат таблицы Courses")

            cursor.execute(f"""CREATE TABLE IF NOT EXISTS StudentGroups
                                    SELECT * FROM StudentGroups_tmp;""")
            print("Откат таблицы StudentGroups")

            cursor.execute(f"""CREATE TABLE IF NOT EXISTS Students
                                    SELECT * FROM Students_tmp;""")
            print("Откат таблицы Students")

    def get_all_groups_name(self):
        with self.connection.cursor() as cursor:
            cursor.execute("SELECT group_name FROM StudentGroups;")
            return [group['group_name'] for group in cursor.fetchall()]

    def get_total_students(self):
        with self.connection.cursor() as cursor:
            cursor.execute("""SELECT COUNT(student_id) as count FROM Students""")
            return cursor.fetchone()['count']

    def get_total_groups(self):
        with self.connection.cursor() as cursor:
            cursor.execute("""SELECT COUNT(group_id) as count FROM StudentGroups""")
            return cursor.fetchone()['count']

    # def _save_partial_result(self, cursor):
    #     result = []
    #     while True:
    #         partial_result = cursor.fetchmany(100)  # Определите удобный для вас размер пакета
    #
    #         if not partial_result:
    #             break
    #
    #         result.extend(partial_result)
    #     return result

    # def get_different_tables(self):
    #     with self.connection.cursor() as cursor:
    #         # cursor.execute("SHOW VARIABLES;")
    #         # print(cursor.fetchall())
    #
    #         difference = {}
    #
    #         cursor.execute("""-- new groups
    #             SELECT StudentGroups.* FROM StudentGroups LEFT JOIN StudentGroups_tmp
    #                 ON StudentGroups.group_id = StudentGroups_tmp.group_id
    #             WHERE StudentGroups_tmp.group_id IS NULL;""")
    #         difference['new_groups'] = self._save_partial_result(cursor)
    #         print("-- new groups")
    #
    #         cursor.execute("""-- deleted groups
    #             SELECT StudentGroups_tmp.* FROM StudentGroups RIGHT JOIN StudentGroups_tmp
    #                 ON StudentGroups.group_id = StudentGroups_tmp.group_id
    #             WHERE StudentGroups.group_id IS NULL;""")
    #         difference['deleted_groups'] = self._save_partial_result(cursor)
    #         print("-- deleted groups")
    #
    #         cursor.execute("""-- entered students
    #             SELECT Students.student_id,
    #                 Students.student_name,
    #                 Students.student_group AS 'group_id',
    #                 StudentGroups.group_name AS 'group_name',
    #                 Students.leader
    #             FROM Students
    #                 LEFT JOIN Students_tmp ON Students.student_id = Students_tmp.student_id
    #                 JOIN StudentGroups ON Students.student_group = StudentGroups.group_id
    #             WHERE Students_tmp.student_id IS NULL;""")
    #         difference['entered_students'] = self._save_partial_result(cursor)
    #         print("-- entered students")
    #
    #         cursor.execute("""-- left students
    #             SELECT Students_tmp.student_id,
    #                 Students_tmp.student_name,
    #                 Students_tmp.student_group AS 'group_id',
    #                 StudentGroups_tmp.group_name AS 'group_name',
    #                 Students_tmp.leader
    #             FROM Students
    #                 RIGHT JOIN Students_tmp ON Students.student_id = Students_tmp.student_id
    #                 JOIN StudentGroups_tmp ON Students_tmp.student_group = StudentGroups_tmp.group_id
    #             WHERE Students.student_id IS NULL;""")
    #         difference['left_students'] = self._save_partial_result(cursor)
    #         print("-- left students")
    #
    #         cursor.execute("""-- leader status
    #             SELECT Students.student_id,
    #                 Students.student_name,
    #                 CASE
    #                     WHEN Students.leader <> 0 THEN "promotion"
    #                     WHEN Students.leader = 0 THEN "demotion"
    #                 END AS status,
    #                 Students.student_group AS 'group_id',
    #                 StudentGroups.group_name AS 'group_name'
    #             FROM Students -- убираем всех только-что зачисленных студентов
    #                 LEFT JOIN Students_tmp ON Students.student_id = Students_tmp.student_id
    #                 AND Students.leader <> Students_tmp.leader
    #                 JOIN StudentGroups ON Students.student_group = StudentGroups.group_id
    #             WHERE Students_tmp.student_id IS NOT NULL;""")
    #         difference['leader_status'] = self._save_partial_result(cursor)
    #         print("-- leader status")
    #
    #         cursor.execute("""-- group changes
    #             SELECT Students.student_id,
    #                 Students.student_name,
    #                 Students.student_group AS 'new_group_id',
    #                 Students_tmp.student_group AS 'last_group_id',
    #                 StudentGroups.group_name AS 'new_group_name',
    #                 StudentGroups_tmp.group_name AS 'last_group_name'
    #             FROM Students
    #                 LEFT JOIN Students_tmp ON Students.student_id = Students_tmp.student_id
    #                     AND Students.student_group <> Students_tmp.student_group
    #                 JOIN StudentGroups ON Students.student_group = StudentGroups.group_id
    #                 JOIN StudentGroups_tmp ON Students_tmp.student_group = StudentGroups_tmp.group_id
    #             WHERE Students_tmp.student_id IS NOT NULL""")
    #         difference['group_changes'] = self._save_partial_result(cursor)
    #         print("-- group changes")
    #
    #         print("difference объект создан")
    #         return difference

    def _check_existence(self, column, table, value):
        with self.connection.cursor() as cursor:
            if cursor.execute(f"SELECT {column} FROM {table} WHERE {column} = {value};"):
                return True
            else:
                return False

    def save_data(self, chunk_data):
        with self.connection.cursor() as cursor:
            if not self._check_existence("course_id", "Courses", chunk_data['course'][0]):
                cursor.execute(f"""INSERT INTO Courses (course_id, course_name) VALUES (%s, %s);""",
                               (chunk_data['course'][0], chunk_data['course'][1]))

            if not self._check_existence("institute_id", "Institutes", chunk_data['institute'][0]):
                cursor.execute(
                    f"""INSERT INTO Institutes (institute_id, institute_name, institute_num) VALUES (%s, %s, %s);""",
                    (chunk_data['institute'][0], chunk_data['institute'][1], chunk_data['institute_num']))

            if not self._check_existence("group_id", "StudentGroups", chunk_data['group'][0]):
                cursor.execute(
                    f"""INSERT INTO StudentGroups (group_id, group_name, institute, course) VALUES (%s, %s, %s, %s);""",
                    (chunk_data['group'][0], chunk_data['group'][1], chunk_data['institute'][0],
                     chunk_data['course'][0]))

            if not self._check_existence("student_id", "Students", chunk_data['student'][0]):
                cursor.execute(
                    f"""INSERT INTO Students (student_id, student_name, student_group, leader) VALUES (%s, %s, %s, %s);""",
                    (chunk_data['student'][0], chunk_data['student'][1], chunk_data['group'][0], chunk_data['leader']))

            # print(chunk_data)
            self.connection.commit()

    def update_leaders_status(self, chunk_data):
        with self.connection.cursor() as cursor:
            cursor.execute(f"""
UPDATE Students
	JOIN StudentGroups ON Students.student_group = StudentGroups.group_id
SET leader = 1
WHERE StudentGroups.group_name = %s
	AND Students.student_name = %s;""", (chunk_data['group_name'], chunk_data['student_name']))
            self.connection.commit()

    def _get_name_attributes(self, student_id):
        with self.connection.cursor() as cursor:
            cursor.execute(f"""
                SELECT institute_name,
                    course_name,
                    group_name,
                    student_name
                FROM Students_tmp
                    JOIN StudentGroups_tmp ON Students_tmp.student_group = StudentGroups_tmp.group_id
                    JOIN Courses_tmp ON StudentGroups_tmp.course = Courses_tmp.course_id
                    JOIN Institutes_tmp ON StudentGroups_tmp.institute = Institutes_tmp.institute_id
                WHERE Students_tmp.student_id = {student_id};
            """)
            name_attributes = cursor.fetchone()
            return name_attributes

    def archive_report(self, report_txt_file_path, report_json_file_path):
        with open(report_txt_file_path, "r", encoding='utf-8') as f:
            report_txt = f.read()

        with open(report_json_file_path, "r", encoding='utf-8') as f:
            report_json = f.read()

        with self.connection.cursor() as cursor:
            cursor.execute(
                "INSERT INTO ReportArchive (report_content, report_json, report_date) VALUES (%s, %s, CURRENT_DATE());",
                (report_txt, report_json))
            self.connection.commit()
            print("Отчёт загружен в архив")

    def archive_data(self, left_students):
        with self.connection.cursor() as cursor:
            for student in left_students:
                name_attributes = self._get_name_attributes(student['student_id'])
                cursor.execute("""INSERT INTO StudentArchive (institute_name, course_name, group_name, student_name, student_id, record_date)
                    VALUES(%s, %s, %s, %s, %s, CURRENT_DATE());""",
                               (name_attributes['institute_name'],
                                name_attributes['course_name'],
                                name_attributes['group_name'],
                                name_attributes['student_name'],
                                student['student_id']))
                self.connection.commit()
            print("Отчисленные студенты загружены в архив")

    def connection_close(self):
        self.connection.close()
        print("Соединение с базой данных закрыто")