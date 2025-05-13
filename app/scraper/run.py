from asyncio import sleep

from loguru import logger


async def run():
    logger.debug("run function start")
    await sleep(1)
    logger.debug("run function complete")
