import json
from pathlib import Path

from langchain_core.callbacks import CallbackManagerForRetrieverRun
from langchain_core.documents import Document
from langchain_core.retrievers import BaseRetriever
from rank_bm25 import BM25Okapi

from app.backends.base import StorageBackend
from app.config import settings

# Persisted JSON-lines file lives next to the uploads directory
_CHUNKS_FILE = Path(settings.upload_dir).parent / "bm25_chunks.jsonl"


class BM25Retriever(BaseRetriever):
    chunks: list[dict]
    top_k: int = 4

    def _get_relevant_documents(
        self,
        query: str,
        *,
        run_manager: CallbackManagerForRetrieverRun,
    ) -> list[Document]:
        if not self.chunks:
            return []

        tokenized_corpus = [c["content"].lower().split() for c in self.chunks]
        bm25 = BM25Okapi(tokenized_corpus)
        scores = bm25.get_scores(query.lower().split())

        top_indices = sorted(range(len(scores)), key=lambda i: scores[i], reverse=True)[
            : self.top_k
        ]

        return [
            Document(
                page_content=self.chunks[i]["content"],
                metadata={
                    "document_id": self.chunks[i]["document_id"],
                    "filename": self.chunks[i]["filename"],
                    "chunk_index": self.chunks[i]["chunk_index"],
                    "score": float(scores[i]),
                },
            )
            for i in top_indices
            if scores[i] > 0
        ]


class PlaintextBackend(StorageBackend):
    name = "plaintext"

    def __init__(self):
        _CHUNKS_FILE.parent.mkdir(parents=True, exist_ok=True)
        self._chunks: list[dict] = []
        self._load()

    def _load(self):
        if _CHUNKS_FILE.exists():
            with open(_CHUNKS_FILE) as f:
                self._chunks = [json.loads(line) for line in f if line.strip()]

    def _save(self):
        with open(_CHUNKS_FILE, "w") as f:
            for chunk in self._chunks:
                f.write(json.dumps(chunk) + "\n")

    async def ingest(self, document_id: str, filename: str, chunks: list[Document]) -> int:
        new_chunks = [
            {
                "document_id": document_id,
                "filename": filename,
                "chunk_index": i,
                "content": chunk.page_content,
            }
            for i, chunk in enumerate(chunks)
        ]
        self._chunks.extend(new_chunks)
        self._save()
        return len(chunks)

    def get_retriever(self, top_k: int = 4) -> BaseRetriever:
        return BM25Retriever(chunks=list(self._chunks), top_k=top_k)

    async def list_documents(self) -> list[dict]:
        seen: dict[str, dict] = {}
        for chunk in self._chunks:
            doc_id = chunk["document_id"]
            if doc_id not in seen:
                seen[doc_id] = {
                    "document_id": doc_id,
                    "filename": chunk["filename"],
                    "chunk_count": 0,
                }
            seen[doc_id]["chunk_count"] += 1
        return list(seen.values())

    async def delete_document(self, document_id: str) -> bool:
        original_len = len(self._chunks)
        self._chunks = [c for c in self._chunks if c["document_id"] != document_id]
        if len(self._chunks) == original_len:
            return False
        self._save()
        return True
