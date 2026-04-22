from typing import Any

from pydantic import BaseModel

from app.models.requests import DatabaseSettings


class DatabaseResponse(BaseModel):
    id: str
    name: str
    description: str | None = None
    backend_type: str
    created_at: Any = None
    settings: DatabaseSettings | None = None


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


class ChunkResponse(BaseModel):
    chunk_index: int
    content: str


class QueryResponse(BaseModel):
    question: str
    answer: str
    sources: list[SourceDocument]
    backend_used: str
    latency_ms: int


class RoutedDatabase(BaseModel):
    id: str
    name: str
    description: str | None = None


class SmartQueryResponse(BaseModel):
    question: str
    answer: str
    sources: list[SourceDocument]
    routed_databases: list[RoutedDatabase]
    routing_explanation: str
    latency_ms: int


