from app.backends.base import StorageBackend
from app.config import settings

_backends: dict[str, StorageBackend] = {}
_active: str = settings.default_backend


async def init_backends() -> None:
    global _backends, _active
    from app.backends.plaintext_backend import PlaintextBackend
    from app.backends.sql_backend import SQLBackend
    from app.backends.vector_backend import VectorBackend

    _backends = {
        "vector": VectorBackend(),
        "sql": SQLBackend(),
        "plaintext": PlaintextBackend(),
    }
    _active = settings.default_backend


async def shutdown_backends() -> None:
    pass


def get_active_backend() -> StorageBackend:
    return _backends[_active]


def get_backend(name: str) -> StorageBackend:
    if name not in _backends:
        raise KeyError(f"Unknown backend: {name!r}. Available: {list(_backends)}")
    return _backends[name]


def set_active_backend(name: str) -> None:
    global _active
    if name not in _backends:
        raise KeyError(f"Unknown backend: {name!r}. Available: {list(_backends)}")
    _active = name


def list_backends() -> list[dict]:
    return [{"name": name, "active": name == _active} for name in _backends]
