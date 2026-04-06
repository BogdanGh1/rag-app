import os
from dataclasses import dataclass
from pathlib import Path

from rag_backends.base import StorageBackend

BACKEND_NAMES = ["vector", "sql", "plaintext"]

# Per-database backend instances: (user_id, db_id) -> StorageBackend
_db_backends: dict[tuple[str, str], StorageBackend] = {}


@dataclass
class BackendConfig:
    chroma_persist_dir: str
    sqlite_dir: str
    bm25_dir: str
    embedding_model: str
    openai_api_key: str


def list_backend_names() -> list[str]:
    return list(BACKEND_NAMES)


def get_database_backend(
    db_id: str, backend_type: str, user_id: str, config: BackendConfig
) -> StorageBackend:
    """Return (or lazily create) a backend instance scoped to a specific named database."""
    key = (user_id, db_id)
    if key not in _db_backends:
        _db_backends[key] = _create_backend(backend_type, user_id, db_id, config)
    return _db_backends[key]


def evict_database_backend(db_id: str, user_id: str) -> None:
    """Remove a cached backend instance (called when a database is deleted)."""
    _db_backends.pop((user_id, db_id), None)


def _create_backend(
    backend_type: str, user_id: str, db_id: str, config: BackendConfig
) -> StorageBackend:
    if backend_type == "vector":
        from rag_backends.vector_backend import VectorBackend

        return VectorBackend(
            chroma_persist_dir=os.path.join(config.chroma_persist_dir, user_id, db_id),
            embedding_model=config.embedding_model,
            openai_api_key=config.openai_api_key,
        )

    if backend_type == "sql":
        from rag_backends.sql_backend import SQLBackend

        return SQLBackend(db_path=os.path.join(config.sqlite_dir, f"{user_id}_{db_id}.db"))

    if backend_type == "plaintext":
        from rag_backends.plaintext_backend import PlaintextBackend

        return PlaintextBackend(
            chunks_file=Path(config.bm25_dir) / f"{user_id}_{db_id}.jsonl"
        )

    raise KeyError(f"Unknown backend type: {backend_type!r}")
