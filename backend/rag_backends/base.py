from abc import ABC, abstractmethod

from langchain_core.documents import Document
from langchain_core.retrievers import BaseRetriever


class StorageBackend(ABC):
    name: str

    @abstractmethod
    async def ingest(self, document_id: str, filename: str, chunks: list[Document]) -> int:
        """Ingest document chunks. Returns count of chunks stored."""
        ...

    @abstractmethod
    def get_retriever(self, top_k: int = 4) -> BaseRetriever:
        """Return a LangChain-compatible retriever."""
        ...

    @abstractmethod
    async def list_documents(self) -> list[dict]:
        """List all indexed documents with metadata."""
        ...

    @abstractmethod
    async def delete_document(self, document_id: str) -> bool:
        """Delete all chunks for a document. Returns True if anything was deleted."""
        ...
