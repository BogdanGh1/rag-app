import os
from pathlib import Path

from rag_backends.base import StorageBackend

# Named backends available in the system (used for validation and listing)
BACKEND_NAMES = ["vector", "sql", "plaintext"]

# Per-database backend instances: (user_id, db_id) -> StorageBackend
_db_backends: dict[tuple[str, str], StorageBackend] = {}


async def init_backends() -> None:
    """Called at startup — no global instances needed; backends are per-database."""
    pass


def list_backend_names() -> list[str]:
    return list(BACKEND_NAMES)


def get_database_backend(db_id: str, backend_type: str, user_id: str) -> StorageBackend:
    """Return (or lazily create) a backend instance scoped to a specific named database."""
    key = (user_id, db_id)
    if key not in _db_backends:
        _db_backends[key] = _create_backend(backend_type, user_id, db_id)
    return _db_backends[key]


def evict_database_backend(db_id: str, user_id: str) -> None:
    """Remove a cached backend instance (called when a database is deleted)."""
    _db_backends.pop((user_id, db_id), None)


def _create_backend(backend_type: str, user_id: str, db_id: str) -> StorageBackend:
    from app.config import settings

    if backend_type == "vector":
        from rag_backends.vector_backend import VectorBackend

        db_chroma_dir = os.path.join(settings.chroma_persist_dir, user_id, db_id)
        return VectorBackend(
            chroma_persist_dir=db_chroma_dir,
            embedding_model=settings.embedding_model,
            openai_api_key=settings.openai_api_key,
        )

    if backend_type == "sql":
        from rag_backends.sql_backend import SQLBackend

        sqlite_dir = os.path.dirname(os.path.abspath(settings.sqlite_path))
        return SQLBackend(db_path=os.path.join(sqlite_dir, f"{user_id}_{db_id}.db"))

    if backend_type == "plaintext":
        from rag_backends.plaintext_backend import PlaintextBackend

        bm25_dir = Path(settings.upload_dir).parent / "bm25"
        return PlaintextBackend(chunks_file=bm25_dir / f"{user_id}_{db_id}.jsonl")

    raise KeyError(f"Unknown backend type: {backend_type!r}")
