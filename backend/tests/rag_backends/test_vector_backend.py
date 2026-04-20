from unittest.mock import patch

import pytest
from langchain_core.documents import Document
from langchain_core.embeddings import Embeddings

from rag_backends.vector import VectorBackend


class FakeEmbeddings(Embeddings):
    """Deterministic fixed-dimension embeddings for testing (no API calls)."""

    _DIM = 16

    def embed_documents(self, texts: list[str]) -> list[list[float]]:
        return [self._embed(t) for t in texts]

    def embed_query(self, text: str) -> list[float]:
        return self._embed(text)

    def _embed(self, text: str) -> list[float]:
        vec = [0.0] * self._DIM
        for i, c in enumerate(text):
            vec[i % self._DIM] += ord(c) / 1000.0
        norm = sum(x**2 for x in vec) ** 0.5 or 1.0
        return [x / norm for x in vec]


@pytest.fixture
def backend(tmp_path):
    with patch("langchain_openai.OpenAIEmbeddings", return_value=FakeEmbeddings()):
        return VectorBackend(
            chroma_persist_dir=str(tmp_path / "chroma"),
            embedding_model="text-embedding-3-small",
            openai_api_key="sk-fake",
        )


async def test_ingest_returns_chunk_count(backend, make_chunks):
    count = await backend.ingest("doc-1", "test.txt", make_chunks("hello", "world"))
    assert count == 2


async def test_list_documents_after_ingest(backend, make_chunks):
    await backend.ingest("doc-1", "test.txt", make_chunks("hello world"))
    docs = await backend.list_documents()
    assert len(docs) == 1
    assert docs[0]["document_id"] == "doc-1"
    assert docs[0]["filename"] == "test.txt"
    assert docs[0]["chunk_count"] == 1


async def test_list_multiple_documents(backend, make_chunks):
    await backend.ingest("doc-1", "a.txt", make_chunks("foo"))
    await backend.ingest("doc-2", "b.txt", make_chunks("bar", "baz"))
    docs = await backend.list_documents()
    by_id = {d["document_id"]: d for d in docs}
    assert by_id["doc-1"]["chunk_count"] == 1
    assert by_id["doc-2"]["chunk_count"] == 2


async def test_delete_document(backend, make_chunks):
    await backend.ingest("doc-1", "test.txt", make_chunks("hello"))
    assert await backend.delete_document("doc-1") is True
    assert await backend.list_documents() == []


async def test_delete_nonexistent_document(backend):
    assert await backend.delete_document("no-such-doc") is False


async def test_delete_only_removes_target(backend, make_chunks):
    await backend.ingest("doc-1", "a.txt", make_chunks("foo"))
    await backend.ingest("doc-2", "b.txt", make_chunks("bar"))
    await backend.delete_document("doc-1")
    docs = await backend.list_documents()
    assert len(docs) == 1
    assert docs[0]["document_id"] == "doc-2"


async def test_retriever_returns_results(backend, make_chunks):
    await backend.ingest("doc-1", "test.txt", make_chunks("hello world content"))
    results = backend.get_retriever(top_k=1).invoke("hello world")
    assert len(results) >= 1


async def test_retriever_respects_top_k(backend, make_chunks):
    await backend.ingest("doc-1", "a.txt", make_chunks("alpha", "beta", "gamma", "delta", "epsilon"))
    results = backend.get_retriever(top_k=2).invoke("alpha beta")
    assert len(results) <= 2
