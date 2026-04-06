import os
from pathlib import Path

from rag_backends.registry import (
    BACKEND_NAMES,
    BackendConfig,
    StorageBackend,
    evict_database_backend,
    get_database_backend as _get_database_backend,
    list_backend_names,
)


def _config() -> BackendConfig:
    from app.config import settings

    return BackendConfig(
        chroma_persist_dir=settings.chroma_persist_dir,
        sqlite_dir=os.path.dirname(os.path.abspath(settings.sqlite_path)),
        bm25_dir=str(Path(settings.upload_dir).parent / "bm25"),
        embedding_model=settings.embedding_model,
        openai_api_key=settings.openai_api_key,
    )


async def init_backends() -> None:
    pass


def get_database_backend(db_id: str, backend_type: str, user_id: str) -> StorageBackend:
    return _get_database_backend(db_id, backend_type, user_id, _config())


__all__ = [
    "BACKEND_NAMES",
    "init_backends",
    "list_backend_names",
    "get_database_backend",
    "evict_database_backend",
]
