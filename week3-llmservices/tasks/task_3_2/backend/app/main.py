from contextlib import asynccontextmanager

import httpx
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.chat import router as chat_router
from app.core.config import get_settings
from app.core.logging import configure_logging

configure_logging()

@asynccontextmanager
async def lifespan(app: FastAPI):
    settings = get_settings()

    http_client = httpx.AsyncClient(
        timeout=httpx.Timeout(
            timeout=settings.request_timeout
        )
    )

    app.state.http_client = http_client

    yield

    await http_client.aclose()
    
settings = get_settings()


app = FastAPI(

    title=settings.app_name,
    version=settings.app_version,
    description="Weather-aware activity recommendation service",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",
        "http://localhost:5174",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(chat_router)