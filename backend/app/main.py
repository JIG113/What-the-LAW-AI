from fastapi import FastAPI

from app.api.routes import router
from app.core.config import settings
from app.core.db import init_db

app = FastAPI(title=settings.app_name)


@app.on_event("startup")
def on_startup():
    init_db()


app.include_router(router, prefix=settings.api_prefix)


@app.get("/health")
def health():
    return {"status": "ok"}
