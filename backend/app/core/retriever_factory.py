import os
from pathlib import Path

from rag_backends.base import StorageBackend

# Named backends available in the system (used for validation and listing)
BACKEND_NAMES = ["vector", "sql", "plaintext"]

# Per-user backend instances: (user_id, backend_name) -> StorageBackend
_user_backends: dict[tuple[str, str], StorageBackend] = {}


async def init_backends() -> None:
    """Called at startup — no global instances needed; backends are per-user."""
    pass


def get_backend(name: str) -> None:
    """Validate a backend name is known."""
    if name not in BACKEND_NAMES:
        raise KeyError(f"Unknown backend: {name!r}. Available: {BACKEND_NAMES}")


def list_backend_names() -> list[str]:
    return list(BACKEND_NAMES)


def get_user_backend(name: str, user_id: str) -> StorageBackend:
    """Return (or lazily create) a backend instance scoped to a single user."""
    if name not in BACKEND_NAMES:
        raise KeyError(f"Unknown backend: {name!r}. Available: {BACKEND_NAMES}")

    key = (user_id, name)
    if key not in _user_backends:
        _user_backends[key] = _create_backend(name, user_id)
    return _user_backends[key]


def _create_backend(name: str, user_id: str) -> StorageBackend:
    from app.config import settings

    if name == "vector":
        from rag_backends.vector_backend import VectorBackend

        user_chroma_dir = os.path.join(settings.chroma_persist_dir, user_id)
        return VectorBackend(
            chroma_persist_dir=user_chroma_dir,
            embedding_model=settings.embedding_model,
            openai_api_key=settings.openai_api_key,
        )

    if name == "sql":
        from rag_backends.sql_backend import SQLBackend

        sqlite_dir = os.path.dirname(os.path.abspath(settings.sqlite_path))
        return SQLBackend(db_path=os.path.join(sqlite_dir, f"{user_id}.db"))

    if name == "plaintext":
        from rag_backends.plaintext_backend import PlaintextBackend

        bm25_dir = Path(settings.upload_dir).parent / "bm25"
        return PlaintextBackend(chunks_file=bm25_dir / f"{user_id}.jsonl")

    raise KeyError(f"Unknown backend: {name!r}")
