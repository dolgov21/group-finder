from json import loads
from pprint import pprint
from collections import deque
from bs4 import BeautifulSoup
from fake_useragent import UserAgent
import requests
from time import sleep

from server.apps.shared.models import Institute, Group, Student


class Crawler:
    CONNECTION_TIMEOUT = 5.5
    MAX_POOL_SIZE = 5
    TIME_DELTA = 1.0
    MAX_EXCEPTION_COUNT = 5
    RECURSION_LIMIT = 3

    KAI_INSTITUTES = {
        1: "Институт авиации, наземного транспорта и энергетики",  # отделение СПО ТК 8
        2: "Факультет физико-математический",
        3: "Институт автоматики и электронного приборостроения",
        4: "Институт компьютерных технологий и защиты информации",  # отделение СПО КИТ 4
        5: "Институт радиоэлектроники, фотоники и цифровых технологий",
        6: "Институт инженерной экономики и предпринимательства"
    }

    def __init__(self):
        self.exception_counter = 0
        self.recursions_count = 0

    def __get_random_headers(self):
        return {
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7',
            'User-Agent': UserAgent().random,
            'Accept-Language': 'ru-RU,ru;q=0.9,en-US;q=0.8,en;q=0.7',
            'Accept-Encoding': 'gzip, deflate, br',
            'Cache-Control': 'max-age=0'
        }

    def take_institutes(self):
        for key, value in self.KAI_INSTITUTES.items():
            obj = Institute.objects.create(name=value, institute_num=key)
            print(obj)

    def take_groups(self) -> list[Group]:
        url = "https://kai.ru/web/studentu/raspisanie1" 
        params = {
            "p_p_id": "pubStudentSchedule_WAR_publicStudentSchedule10",
            "p_p_lifecycle": 2,
            "p_p_state": "normal",
            "p_p_mode": "view",
            "p_p_resource_id": "getGroupsURL",
            "p_p_cacheability": "cacheLevelPage",
            "p_p_col_id": "column-1",
            "p_p_col_count": 1
        }
        while True:
            try:
                response = requests.get(url=url, params=params, headers=self.__get_random_headers())
                response.raise_for_status()
                groups_data = loads(response.text)[0:36:1]

                for group_data in groups_data:
                    institute_num = int(
                        "1" if group_data['group'].startswith('8') else
                        group_data['group'][0]
                    )
                    institute = Institute.objects.get(institute_num=institute_num)

                    obj = Group.objects.create(
                        id=group_data['id'],
                        group=group_data['group'],
                        course=group_data['group'][1],
                        institute=institute
                    )
                    print(obj)
                break
            except requests.exceptions.Timeout:
                print(f"Recursion parsing groups {self.recursions_count}: ")
                if self.recursions_count > self.RECURSION_LIMIT:
                    raise Exception(f"The recursion limit has been reached: {self.recursions_count}")
                else:
                    print("TimeoutError in get_groups query\n")
                    sleep(self.CONNECTION_TIMEOUT)
                    self.recursions_count += 1
            except requests.exceptions.RequestException as e:
                print(f"RequestException: {e}")
                raise

    def get_students_from_group(self, group: Group) -> list[Student]:
        url = "https://kai.ru/infoClick/-/info/group" 
        params = {
            "id": group.id,
            "name": group.group
        }
        students: list[Student] = list()
        try:
            response = requests.get(url=url, params=params, headers=self.__get_random_headers())
            response.raise_for_status()
            group_page = response.text
            soup = BeautifulSoup(group_page, "html.parser")

            table = soup.find("tbody")
            if table is None:
                alert = soup.find("div", class_="alert alert-info")
                if alert is None:
                    print("table tag is NoneType, why?", group.group)
                    self.groups.append(group)
                    self.exception_counter += 1
                    print(list(self.groups)[-1])
                    return []
                else:
                    print(group.group, "is", alert.text)
                    return []

            trows = table.find_all("tr")
            for trow in trows:
                tcolumns = trow.find_all("td")
                student_column = tcolumns[1]
                student = student_column.find(text=True, recursive=False).get_text(strip=True)
                
                leader = True if student_column.find("span") is not None else False
                institute = Institute.objects.get(institute_num=group.institute.institute_num)

                obj = Student.objects.create(
                    student=student,
                    leader=leader,
                    institute=institute,
                    group=group
                )
                print(obj)
        except requests.exceptions.Timeout:
            self.exception_counter += 1
            print(f"TimeoutError in group: id->{group.id} group->{group.group}")
            print(f"groups in groups_queue: xxx")
        except requests.exceptions.RequestException as e:
            print(f"RequestException: {e}")
        return students

    def take_students(self):
        groups = list(Group.objects.all())
        for group in groups:
            results = self.get_students_from_group(group=group)

            if self.exception_counter > self.MAX_EXCEPTION_COUNT:
                raise Exception("self.exception_counter more than the allowed limit!")

            pprint(results)

            students = list()  # [1, 2, 3, 2, 0, 23, 4]
            for r_list in results:
                if not r_list:
                    continue
                for r in r_list:
                    students.append(r)

            print(f"\nreturned {len(students)} students")
            print(f"groups in queue: xxx, "
                  f"exception_counter={self.exception_counter}/{self.MAX_EXCEPTION_COUNT}")

            sleep(self.TIME_DELTA)

    def get_data(self):
        self.take_institutes()
        self.take_groups()
        self.take_students()