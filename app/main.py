import uvicorn
from config import settings
from fastapi import FastAPI
from loguru import logger


app = FastAPI()


@app.get("/")
async def root() -> dict[str, str]:
    logger.debug("root page logic...")
    return {"message": "This is a root page"}


if __name__ == "__main__":
    logger.add(
        settings.logger.logbook_path,
        format=settings.logger.logs_format,
        rotation=settings.logger.rotation_time,
        compression="zip",
        enqueue=True,
    )
    logger.debug("The logger has been configured")

    logger.debug("Uvicorn gets to work...")
    uvicorn.run("app.main:app")
