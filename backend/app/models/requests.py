from typing import Literal

from pydantic import BaseModel, Field


class QueryRequest(BaseModel):
    question: str
    backend: Literal["vector", "sql", "plaintext"]
    top_k: int = Field(default=4, ge=1, le=20)
    llm_model: str | None = None
