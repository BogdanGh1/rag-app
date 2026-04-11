from pydantic import BaseModel, Field


class CreateDatabaseRequest(BaseModel):
    name: str
    description: str | None = None
    backend_type: str  # vector | sql | plaintext


class QueryRequest(BaseModel):
    question: str
    db_id: str
    top_k: int = Field(default=4, ge=1, le=20)
    llm_model: str | None = None
