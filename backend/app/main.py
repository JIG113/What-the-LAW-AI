from contextlib import asynccontextmanager

from fastapi import FastAPI

from app.api.routes import router
from app.core.config import settings
from app.core.db import init_db


@asynccontextmanager
async def lifespan(_: FastAPI):
    init_db()
    yield


app = FastAPI(
    title=settings.app_name,
    lifespan=lifespan,
    swagger_ui_parameters={
        "docExpansion": "none",
        "defaultModelsExpandDepth": -1,
        "displayRequestDuration": True,
    },
)
app.include_router(router, prefix=settings.api_prefix)


@app.get("/health")
def health():
    return {"status": "ok"}


@app.get("/")
def root():
    return {
        "service": settings.app_name,
        "status": "running",
        "health": "/health",
        "docs": "/docs",
        "api_base": settings.api_prefix,
        "guide": [
            "1) /docs 로 이동",
            "2) 문서 업로드 실행",
            "3) 분석 실행",
            "4) 분석 결과 조회",
        ],
    }
