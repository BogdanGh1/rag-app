import pytest
from langchain_core.documents import Document

from rag_backends.plaintext_backend import PlaintextBackend


@pytest.fixture
def backend(tmp_path):
    return PlaintextBackend(chunks_file=tmp_path / "chunks.jsonl")


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
    # Need ≥3 docs so BM25 IDF is positive for a term in 1 doc
    await backend.ingest("doc-1", "a.txt", [Document(page_content="python programming language")])
    await backend.ingest("doc-2", "b.txt", [Document(page_content="cooking pasta carbonara")])
    await backend.ingest("doc-3", "c.txt", [Document(page_content="financial markets investing")])
    results = backend.get_retriever(top_k=1).invoke("python")
    assert len(results) == 1
    assert "python" in results[0].page_content.lower()


async def test_retriever_returns_empty_on_no_match(backend, make_chunks):
    await backend.ingest("doc-1", "a.txt", make_chunks("hello world"))
    # BM25 returns score=0 for terms not in corpus, which are filtered out
    results = backend.get_retriever().invoke("zzzzzzzzz")
    assert results == []


async def test_retriever_empty_store(backend):
    assert backend.get_retriever().invoke("anything") == []


async def test_persistence(tmp_path, make_chunks):
    chunks_file = tmp_path / "chunks.jsonl"
    b1 = PlaintextBackend(chunks_file=chunks_file)
    await b1.ingest("doc-1", "test.txt", make_chunks("hello world"))

    b2 = PlaintextBackend(chunks_file=chunks_file)
    docs = await b2.list_documents()
    assert len(docs) == 1
    assert docs[0]["document_id"] == "doc-1"
