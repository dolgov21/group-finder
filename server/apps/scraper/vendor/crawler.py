import logging
import json
from typing import List, Dict
from collections import deque
from bs4 import BeautifulSoup
from fake_useragent import UserAgent
import requests
from time import sleep

from ..exceptions import ExceptionLimitExceeded
from server.apps.shared.models import Institute, Group, Student


logger = logging.getLogger("scraper")


class Crawler:
    CONNECTION_TIMEOUT: float = 5.5
    MAX_POOL_SIZE: int = 5
    TIME_DELTA: float = 1.0
    MAX_EXCEPTION_COUNT: int = 5
    RECURSION_LIMIT: int = 3

    INSTITUTES_MAP: Dict[int, str] = {
        1: "Институт авиации, наземного транспорта и энергетики",
        2: "Факультет физико-математический",
        3: "Институт автоматики и электронного приборостроения",
        4: "Институт компьютерных технологий и защиты информации",
        5: "Институт радиоэлектроники, фотоники и цифровых технологий",
        6: "Институт инженерной экономики и предпринимательства"
    }

    def __init__(self):
        self.exception_counter: int = 0
        self.recursion_count: int = 0

    def _get_headers(self) -> Dict[str, str]:
        return {
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
            'User-Agent': UserAgent().random,
            'Accept-Language': 'ru-RU,ru;q=0.9,en-US;q=0.8,en;q=0.7',
            'Cache-Control': 'max-age=0'
        }

    def fetch_institutes(self) -> None:
        """Создает записи институтов в базе данных"""
        for code, name in self.INSTITUTES_MAP.items():
            Institute.objects.create(name=name, institute_code=code)
            logger.debug(f"Processed institute: {name}")

    def fetch_groups(self) -> List[Group]:
        """Получает список учебных групп"""
        url: str = "https://kai.ru/web/studentu/raspisanie1" 
        params: Dict[str, str] = {
            "p_p_id": "pubStudentSchedule_WAR_publicStudentSchedule10",
            "p_p_lifecycle": "2",
            "p_p_state": "normal",
            "p_p_mode": "view",
            "p_p_resource_id": "getGroupsURL",
            "p_p_cacheability": "cacheLevelPage",
            "p_p_col_id": "column-1",
            "p_p_col_count": "1"
        }
        
        while True:
            try:
                response = requests.get(url, params=params, headers=self._get_headers(), timeout=self.CONNECTION_TIMEOUT)
                response.raise_for_status()
                logger.debug(f"Successful get groups list from: {response.url}")

                groups_data = json.loads(response.text)[:36]
                groups = []
                for group_info in groups_data:
                    institute_code = 1 if group_info['group'].startswith('8') else int(group_info['group'][0])
                    institute = Institute.objects.get(institute_code=institute_code)
                    
                    group, created = Group.objects.get_or_create(
                        id=group_info['id'],
                        defaults={
                            'name': group_info['group'],
                            'course': group_info['group'][1],
                            'institute': institute
                        }
                    )
                    if created:
                        groups.append(group)
                        logger.debug(f"Created group: {group}")
                return groups
                
            except requests.exceptions.Timeout:
                self._handle_timeout(group, "fetch_groups")
            except requests.exceptions.RequestException as e:
                logger.error(f"Request error: {e}")
                raise e

    def fetch_students(self, group: Group):
        """Получает список студентов для группы"""
        url: str = "https://kai.ru/infoClick/-/info/group" 
        params: Dict[str, str] = {"id": group.id, "group": group.name}
        
        try:
            response = requests.get(url, params=params, headers=self._get_headers(), timeout=self.CONNECTION_TIMEOUT)
            response.raise_for_status()
            soup = BeautifulSoup(response.text, "html.parser")
            
            table = soup.find("tbody")
            if not table:
                logger.warning(f"No student data for group {group.name}")
                return []
            
            students = []
            for row in table.find_all("tr"):
                columns = row.find_all("td")
                if len(columns) < 2:
                    continue
                
                student_name = columns[1].get_text(strip=True)
                is_leader = bool(columns[1].find("span"))
                
                student, created = Student.objects.get_or_create(
                    id=None,
                    defaults={
                        'name': student_name,
                        'is_leader': is_leader,
                        'group': group,
                        'institute': group.institute
                    }
                )
                if created:
                    students.append(student)
                    logger.debug(f"Created student: {student} / {response.url}")
            return students
            
        except requests.exceptions.Timeout:
            self._handle_timeout(group, f"fetch_students group: {group.name}")
        except requests.exceptions.RequestException as e:
            logger.error(f"Error fetching students for {group.name}: {e}")

    def process_all(self) -> None:
        """Основной метод обработки данных"""
        self.fetch_institutes()
        self.groups_queue = deque(self.fetch_groups())
        
        while len(self.groups_queue) != 0:
            group = self.groups_queue.pop()
            students = self.fetch_students(group)

            if students is not None:
                logger.info(f"Processed {len(students)} students for {group.name}")
            
            sleep(self.TIME_DELTA)
            
            if self.exception_counter > self.MAX_EXCEPTION_COUNT:
                logger.error("Maximum exception count reached!")
                raise ExceptionLimitExceeded("Too many exceptions occurred during processing")

    def _handle_timeout(self, group: Group, context: str) -> None:
        """Обработка таймаутов"""
        self.recursion_count += 1
        self.groups_queue.appendleft(group)

        logger.warning(f"Timeout in {context} (attempt {self.recursion_count})")
        
        if self.recursion_count > self.RECURSION_LIMIT:
            raise RecursionError(f"Recursion limit reached in {context}")
        
        sleep(self.CONNECTION_TIMEOUT)