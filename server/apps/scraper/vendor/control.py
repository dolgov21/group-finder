from threading import Thread

from .crawler import Crawler
from server.apps.scraper.repo import clear_all_tables


def run():
    # run -> crawler -> analyzer -> rapporteur
    clear_all_tables()

    crawler = Crawler()
    thread = Thread(target=crawler.process_all)
    thread.start()
