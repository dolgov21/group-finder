import uvicorn
from fastapi import FastAPI
from loguru import logger


app = FastAPI()


@app.get("/")
async def root() -> dict[str, str]:
    logger.debug("root page logic...")
    return {"message": "This is a root page"}


if __name__ == "__main__":
    logger.add(
        "logs/logbook.log",
        format="{time} {level} {module}:{line} {message}",
        rotation="08:00",
        compression="zip",
        enqueue=True,
    )
    logger.debug("The logger has been configured")

    logger.debug("Uvicorn gets to work...")
    uvicorn.run("app.main:app")
    logger.debug("Uvicorn got to work!")
