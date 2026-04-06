from typing import Literal

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    openai_api_key: str = ""
    llm_model: str = "gpt-4o-mini"
    embedding_model: str = "text-embedding-3-small"
    default_backend: Literal["vector", "sql", "plaintext"] = "vector"

    chroma_persist_dir: str = "./storage/chroma"
    sqlite_path: str = "./storage/sqlite/rag.db"
    upload_dir: str = "./storage/uploads"

    host: str = "0.0.0.0"
    port: int = 8000
    cors_origins: list[str] = ["http://localhost:5173"]
    anonymized_telemetry: bool = False

    database_url: str = "postgresql+asyncpg://rag:rag@localhost:5432/rag"
    secret_key: str = "change-me-in-production-use-a-long-random-string"
    access_token_expire_minutes: int = 60 * 24  # 24 hours


settings = Settings()
