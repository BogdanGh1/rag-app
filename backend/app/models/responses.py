from typing import Any

from pydantic import BaseModel


class UploadResponse(BaseModel):
    document_id: str
    filename: str
    chunk_count: int
    backend: str


class DocumentListResponse(BaseModel):
    document_id: str
    filename: str
    chunk_count: int
    created_at: Any = None


class SourceDocument(BaseModel):
    document_id: str
    filename: str
    content_preview: str
    score: float | None = None


class QueryResponse(BaseModel):
    question: str
    answer: str
    sources: list[SourceDocument]
    backend_used: str
    latency_ms: int


class BackendInfo(BaseModel):
    name: str
    active: bool


class BackendsResponse(BaseModel):
    backends: list[BackendInfo]
    active: str
