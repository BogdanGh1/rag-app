import pytest
from langchain_core.documents import Document

from rag_backends.sql_backend import SQLBackend


@pytest.fixture
def backend(tmp_path):
    return SQLBackend(db_path=str(tmp_path / "test.db"))


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


async def test_retriever_finds_relevant_doc(backend):
    await backend.ingest("doc-1", "a.txt", [Document(page_content="machine learning algorithms")])
    await backend.ingest("doc-2", "b.txt", [Document(page_content="cooking pasta carbonara")])
    results = backend.get_retriever(top_k=1).invoke("machine learning")
    assert len(results) >= 1
    assert results[0].metadata["document_id"] == "doc-1"


async def test_retriever_empty_store(backend):
    assert backend.get_retriever().invoke("anything") == []


async def test_retriever_respects_top_k(backend, make_chunks):
    await backend.ingest("doc-1", "a.txt", make_chunks("foo bar", "foo baz", "foo qux"))
    results = backend.get_retriever(top_k=2).invoke("foo")
    assert len(results) <= 2


async def test_retriever_handles_special_fts5_chars(backend, make_chunks):
    await backend.ingest("doc-1", "a.txt", make_chunks("some content here"))
    # FTS5 syntax chars should not raise
    results = backend.get_retriever().invoke('"quoted query"')
    assert isinstance(results, list)


async def test_ingest_chunk_metadata(backend, make_chunks):
    await backend.ingest("doc-1", "test.txt", make_chunks("alpha", "beta"))
    results = backend.get_retriever(top_k=5).invoke("alpha")
    assert any(r.metadata["document_id"] == "doc-1" for r in results)
    assert any(r.metadata["filename"] == "test.txt" for r in results)
