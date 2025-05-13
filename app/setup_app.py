from apscheduler.schedulers.asyncio import AsyncIOScheduler
from config import settings
from loguru import logger
from scraper.run import run


def setup_logger():
    logger.add(
        settings.logger.logbook_path,
        format=settings.logger.logs_format,
        rotation=settings.logger.rotation_time,
        compression="zip",
        enqueue=True,
    )
    logger.debug("The logger has been configured")


def setup_scraper_scheduler():
    logger.debug("Setup scrapper scheduler")
    scheduler = AsyncIOScheduler()
    scheduler.add_job(run, "cron", minute="1-59")
    scheduler.start()
