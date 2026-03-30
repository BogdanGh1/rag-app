from pathlib import Path

from rag_backends.base import StorageBackend

_backends: dict[str, StorageBackend] = {}


async def init_backends() -> None:
    global _backends
    from app.config import settings
    from rag_backends.plaintext_backend import PlaintextBackend
    from rag_backends.sql_backend import SQLBackend
    from rag_backends.vector_backend import VectorBackend

    _backends = {
        "vector": VectorBackend(
            chroma_persist_dir=settings.chroma_persist_dir,
            embedding_model=settings.embedding_model,
            openai_api_key=settings.openai_api_key,
        ),
        "sql": SQLBackend(db_path=settings.sqlite_path),
        "plaintext": PlaintextBackend(
            chunks_file=Path(settings.upload_dir).parent / "bm25_chunks.jsonl",
        ),
    }


def get_backend(name: str) -> StorageBackend:
    if name not in _backends:
        raise KeyError(f"Unknown backend: {name!r}. Available: {list(_backends)}")
    return _backends[name]


def list_backend_names() -> list[str]:
    return list(_backends.keys())
