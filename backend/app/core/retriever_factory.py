from app.backends.base import StorageBackend

_backends: dict[str, StorageBackend] = {}


async def init_backends() -> None:
    global _backends
    from app.backends.plaintext_backend import PlaintextBackend
    from app.backends.sql_backend import SQLBackend
    from app.backends.vector_backend import VectorBackend

    _backends = {
        "vector": VectorBackend(),
        "sql": SQLBackend(),
        "plaintext": PlaintextBackend(),
    }


def get_backend(name: str) -> StorageBackend:
    if name not in _backends:
        raise KeyError(f"Unknown backend: {name!r}. Available: {list(_backends)}")
    return _backends[name]


def list_backend_names() -> list[str]:
    return list(_backends.keys())
