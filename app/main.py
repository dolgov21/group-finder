import uvicorn
from fastapi import FastAPI


app = FastAPI()


@app.get("/")
async def root():
    return {"message": "This is a root page"}


if __name__ == "__main__":
    uvicorn.run("app.main:app")
