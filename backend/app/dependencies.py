from typing import Annotated

from fastapi import Depends, Query
from langchain_core.retrievers import BaseRetriever

from rag_backends.base import StorageBackend
from app.core.retriever_factory import get_active_backend as _get_active


def active_backend() -> StorageBackend:
    return _get_active()


def retriever_dep(
    backend: Annotated[StorageBackend, Depends(active_backend)],
    top_k: int = Query(default=4, ge=1, le=20),
) -> BaseRetriever:
    return backend.get_retriever(top_k=top_k)
