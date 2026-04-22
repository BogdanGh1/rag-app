import os

from langchain_core.documents import Document
from langchain_core.retrievers import BaseRetriever

from rag_backends.base import StorageBackend


class VectorBackend(StorageBackend):
    name = "vector"

    def __init__(self, *, chroma_persist_dir: str, embedding_model: str, openai_api_key: str):
        from langchain_chroma import Chroma
        from langchain_openai import OpenAIEmbeddings

        os.makedirs(chroma_persist_dir, exist_ok=True)
        embeddings = OpenAIEmbeddings(model=embedding_model, api_key=openai_api_key)
        self._store = Chroma(
            collection_name="rag_documents",
            embedding_function=embeddings,
            persist_directory=chroma_persist_dir,
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

    async def get_chunks(self, document_id: str) -> list[dict]:
        results = self._store.get(
            where={"document_id": document_id},
            include=["documents", "metadatas"],
        )
        chunks = []
        for i, (doc, meta) in enumerate(zip(results["documents"] or [], results["metadatas"] or [])):
            chunks.append({"chunk_index": meta.get("chunk_index", i), "content": doc})
        chunks.sort(key=lambda c: c["chunk_index"])
        return chunks
