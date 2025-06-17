from fastapi import FastAPI
from routers.routes import router

app = FastAPI()


@app.get("/health")
async def read_root():
    return {"message": "Welcome to the Translation App!"}

app.include_router(router, prefix="/api", tags=["translation"])