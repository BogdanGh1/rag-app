from pydantic import BaseModel, Field


class ChunkSettings(BaseModel):
    chunk_size: int = Field(default=800, ge=100, le=8000)
    chunk_overlap: int = Field(default=100, ge=0, le=2000)
    section_based: bool = False


class DatabaseSettings(BaseModel):
    chunk: ChunkSettings | None = None


class CreateDatabaseRequest(BaseModel):
    name: str
    description: str | None = None
    backend_type: str  # vector | sql | plaintext
    settings: DatabaseSettings | None = None


class UpdateDatabaseRequest(BaseModel):
    name: str | None = None
    description: str | None = None
    settings: DatabaseSettings | None = None


class QueryRequest(BaseModel):
    question: str
    db_id: str
    top_k: int = Field(default=4, ge=1, le=20)
    llm_model: str | None = None


class SmartQueryRequest(BaseModel):
    question: str
    top_k: int = Field(default=4, ge=1, le=20)
    llm_model: str | None = None
