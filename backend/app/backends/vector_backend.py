import os

from langchain_core.documents import Document
from langchain_core.retrievers import BaseRetriever

from app.backends.base import StorageBackend
from app.config import settings


def _get_embeddings():
    from langchain_openai import OpenAIEmbeddings

    return OpenAIEmbeddings(
        model=settings.embedding_model,
        api_key=settings.openai_api_key,
    )


class VectorBackend(StorageBackend):
    name = "vector"

    def __init__(self):
        from langchain_chroma import Chroma

        os.makedirs(settings.chroma_persist_dir, exist_ok=True)
        self._embeddings = _get_embeddings()
        self._store = Chroma(
            collection_name="rag_documents",
            embedding_function=self._embeddings,
            persist_directory=settings.chroma_persist_dir,
        )

    async def ingest(self, document_id: str, filename: str, chunks: list[Document]) -> int:
        for chunk in chunks:
            chunk.metadata["document_id"] = document_id
            chunk.metadata["filename"] = filename
        self._store.add_documents(chunks)
        return len(chunks)

    def get_retriever(self, top_k: int = 4) -> BaseRetriever:
        return self._store.as_retriever(search_kwargs={"k": top_k})

    async def list_documents(self) -> list[dict]:
        results = self._store.get(include=["metadatas"])
        seen: dict[str, dict] = {}
        for meta in results.get("metadatas") or []:
            if not meta:
                continue
            doc_id = meta.get("document_id", "unknown")
            if doc_id not in seen:
                seen[doc_id] = {
                    "document_id": doc_id,
                    "filename": meta.get("filename", "unknown"),
                    "chunk_count": 0,
                }
            seen[doc_id]["chunk_count"] += 1
        return list(seen.values())

    async def delete_document(self, document_id: str) -> bool:
        results = self._store.get(where={"document_id": document_id})
        if not results["ids"]:
            return False
        self._store.delete(ids=results["ids"])
        return True
