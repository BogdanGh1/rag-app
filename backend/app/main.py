import os
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.router import api_router
from app.config import settings
from app.core.retriever_factory import init_backends
from app.db import models  # noqa: F401 — registers models with Base metadata
from app.db.database import Base, engine
from app.db.mongo import close_mongo, connect_mongo

os.environ["ANONYMIZED_TELEMETRY"] = str(settings.anonymized_telemetry)


@asynccontextmanager
async def lifespan(app: FastAPI):
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    await init_backends()
    await connect_mongo()
    yield
    await close_mongo()


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
