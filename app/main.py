from contextlib import asynccontextmanager

import uvicorn
from fastapi import FastAPI
from loguru import logger
from setup_app import setup_logger, setup_scraper_scheduler


@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.debug("Application startup...")
    setup_logger()
    setup_scraper_scheduler()
    yield
    logger.debug("Application down.")


app = FastAPI(lifespan=lifespan)


@app.get("/")
async def root() -> dict[str, str]:
    logger.debug("root page logic...")
    return {"message": "This is a root page"}


if __name__ == "__main__":
    uvicorn.run("main:app", app_dir="app")
