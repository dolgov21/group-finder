import json
from datetime import date
from pandasql import sqldf
from sqlalchemy import create_engine, URL
import pandas as pd

class DataAnalyzer(object):
    engine = None

    def __init__(self, host: str, port: int, user: str, password: str, database: str):
        self.host = host
        self.user = user
        self.port = port
        self.password = password
        self.database = database

    def create_engine(self):
        try:
            self.engine = create_engine(URL.create(
                drivername="mysql+pymysql",
                username=self.user,
                password=self.password,
                host=self.host,
                database=self.database))
            print(f"Движок алхимии успешно создан")
        except Exception as ex:
            print(f"Не удалось создать движок алхимии: {ex}")
            exit()
            # raise ex

    def get_different_tables(self):
        StudentGroups = pd.read_sql_table("StudentGroups", con=self.engine)
        StudentGroups_tmp = pd.read_sql_table("StudentGroups_tmp", con=self.engine)
        Students = pd.read_sql_table("Students", con=self.engine)
        Students_tmp = pd.read_sql_table("Students_tmp", con=self.engine)

        difference = {}

        new_groups_df = sqldf("""-- new groups
                SELECT StudentGroups.* FROM StudentGroups LEFT JOIN StudentGroups_tmp
                    ON StudentGroups.group_id = StudentGroups_tmp.group_id
                WHERE StudentGroups_tmp.group_id IS NULL;""")

        difference['new_groups'] = new_groups_df.to_dict('records')
        print("-- new groups")

        deleted_groups_df = sqldf("""-- deleted groups
            SELECT StudentGroups_tmp.* FROM StudentGroups RIGHT JOIN StudentGroups_tmp
                ON StudentGroups.group_id = StudentGroups_tmp.group_id
            WHERE StudentGroups.group_id IS NULL;""")
        difference['deleted_groups'] = deleted_groups_df.to_dict('records')
        print("-- deleted groups")

        entered_students_df = sqldf("""-- entered students
            SELECT Students.student_id,
                Students.student_name,
                Students.student_group AS 'group_id',
                StudentGroups.group_name AS 'group_name',
                Students.leader
            FROM Students
                LEFT JOIN Students_tmp ON Students.student_id = Students_tmp.student_id
                JOIN StudentGroups ON Students.student_group = StudentGroups.group_id
            WHERE Students_tmp.student_id IS NULL;""")
        difference['entered_students'] = entered_students_df.to_dict('records')
        print("-- entered students")

        left_students_df = sqldf("""-- left students
            SELECT Students_tmp.student_id,
                Students_tmp.student_name,
                Students_tmp.student_group AS 'group_id',
                StudentGroups_tmp.group_name AS 'group_name',
                Students_tmp.leader
            FROM Students
                RIGHT JOIN Students_tmp ON Students.student_id = Students_tmp.student_id
                JOIN StudentGroups_tmp ON Students_tmp.student_group = StudentGroups_tmp.group_id
            WHERE Students.student_id IS NULL;""")
        difference['left_students'] = left_students_df.to_dict('records')
        print("-- left students")

        leader_status_df = sqldf("""-- leader status
            SELECT Students.student_id,
                Students.student_name,
                CASE
                    WHEN Students.leader <> 0 THEN "promotion"
                    WHEN Students.leader = 0 THEN "demotion"
                END AS status,
                Students.student_group AS 'group_id',
                StudentGroups.group_name AS 'group_name'
            FROM Students -- убираем всех только-что зачисленных студентов
                JOIN Students_tmp ON Students.student_id = Students_tmp.student_id
                AND Students.leader <> Students_tmp.leader
                JOIN StudentGroups ON Students.student_group = StudentGroups.group_id;""")
        difference['leader_status'] = leader_status_df.to_dict('records')
        print("-- leader status")

        group_changes_df = sqldf("""-- group changes
            SELECT Students.student_id,
                Students.student_name,
                Students.student_group AS 'new_group_id',
                Students_tmp.student_group AS 'last_group_id',
                StudentGroups.group_name AS 'new_group_name',
                StudentGroups_tmp.group_name AS 'last_group_name'
            FROM Students
                JOIN Students_tmp ON Students.student_id = Students_tmp.student_id
                    AND Students.student_group <> Students_tmp.student_group
                JOIN StudentGroups ON Students.student_group = StudentGroups.group_id
                JOIN StudentGroups_tmp ON Students_tmp.student_group = StudentGroups_tmp.group_id;""")
        difference['group_changes'] = group_changes_df.to_dict('records')
        print("-- group changes")

        print("difference объект создан")
        # print(difference)
        return difference

    def _save_report_json(self, difference: dict):
        file_name = f"report_{date.today()}.json"
        file_path = f"reports/json/{file_name}"
        with open(file_path, "w", encoding="utf-8") as file:
            json.dump(difference, file, ensure_ascii=False)
        print(f"difference объект сохранён как {file_name}")
        return file_path

    def _save_report_txt(self, report: str):
        file_name = f"report_{date.today()}.txt"
        file_path = f"reports/txt/{file_name}"
        with open(file_path, "w", encoding="utf-8") as file:
            file.write(report)
        print(f"report объект сохранён как {file_name}")
        return file_path

    def _get_time_difference(self, start_time: int, end_time: int):
        time_difference = end_time - start_time
        hours = str(time_difference // (60*60)).rjust(2, '0')
        minutes = str(time_difference // 60).zfill(2)
        seconds = str(time_difference % 60).zfill(2)
        return f"{hours}:{minutes}:{seconds}"

    def get_report_txt(self, differences: dict, start_time: int, end_time: int, total_students: int, total_groups: int):
        all_new_groups = "\n".join([str(group["group_name"]) for group in differences["new_groups"]])
        all_deleted_groups = "\n".join([str(group["group_name"]) for group in differences["deleted_groups"]])

        all_entered_students = "\n".join([str(student["student_name"]) + " - " + str(student["group_name"]) for student in differences["entered_students"]])
        all_left_students = "\n".join([str(student["student_name"]) + " - " + str(student["group_name"]) for student in differences["left_students"]])

        all_leaders_status_changes = "\n".join([str(student["student_name"] + " - " + str(student["group_name"]) + " - " + ("повышение" if str(student["status"]) == "promotion" else ("понижение" if str(student["status"]) == "demotion" else ""))) for student in differences["leader_status"]])
        all_group_changes = "\n".join([str(student["student_name"] + " - " + str(student["last_group_name"])) + " -> " + str(student["new_group_name"]) for student in differences["group_changes"]])

        report_content = (f'База студентов обновлена: {date.today()}\n'
                          f'Затраченное время: {self._get_time_difference(start_time, end_time)}\n'
                          f'Найдено групп: {total_groups}\n'
                          f'Новые группы: {len(differences["new_groups"])}\n'
                          f'{all_new_groups}\n\n'
                          f'Не найденные группы: {len(differences["deleted_groups"])}\n'
                          f'{all_deleted_groups}\n\n'
                          f'Найдено студентов: {total_students}\n'
                          f'Новые студенты: {len(differences["entered_students"])}\n'
                          f'{all_entered_students}\n\n'
                          f'Не найденные студенты: {len(differences["left_students"])}\n'
                          f'{all_left_students}\n\n'
                          f'Изменения статусов старост: {len(differences["leader_status"])}\n'
                          f'{all_leaders_status_changes}\n\n'
                          f'Студенты изменившие группу: {len(differences["group_changes"])}\n'
                          f'{all_group_changes}\n\n')

        # differences_file_path = self._save_report_json(differences)
        report_txt_file_path = self._save_report_txt(report_content)
        return report_txt_file_path

    def get_report_json(self, differences: dict, start_time: int, end_time: int, total_students: int, total_groups: int):
        report_content = dict(differences)
        report_content["today"] = str(date.today())
        report_content["time_difference"] = self._get_time_difference(start_time, end_time)
        report_content["total_groups"] = total_groups
        report_content["total_new_groups"] = len(differences["new_groups"])
        report_content["total_deleted_groups"] = len(differences["deleted_groups"])
        report_content["total_students"] = total_students
        report_content["total_new_students"] = len(differences["entered_students"])
        report_content["total_deleted_students"] = len(differences["left_students"])
        report_content["total_leader_status"] = len(differences["leader_status"])
        report_content["total_group_changes"] = len(differences["group_changes"])

        report_txt_file_path = self._save_report_json(report_content)
        return report_txt_file_path

