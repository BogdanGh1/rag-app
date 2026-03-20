import os
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.router import api_router
from app.config import settings
from app.core.retriever_factory import init_backends, shutdown_backends

os.environ["ANONYMIZED_TELEMETRY"] = str(settings.anonymized_telemetry)


@asynccontextmanager
async def lifespan(app: FastAPI):
    await init_backends()
    yield
    await shutdown_backends()


app = FastAPI(
    title="RAG App API",
    description="Multi-backend RAG application with ChromaDB, SQLite FTS5, and BM25",
    version="1.0.0",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(api_router, prefix="/api/v1")
