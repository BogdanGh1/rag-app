import uuid
from pathlib import Path

from langchain_core.documents import Document
from langchain_text_splitters import RecursiveCharacterTextSplitter

from rag_backends.base import StorageBackend


def load_documents(file_path: str, filename: str) -> list[Document]:
    suffix = Path(filename).suffix.lower()

    if suffix == ".pdf":
        from langchain_community.document_loaders import PyPDFLoader

        loader = PyPDFLoader(file_path)
    elif suffix in (".docx", ".doc"):
        from langchain_community.document_loaders import Docx2txtLoader

        loader = Docx2txtLoader(file_path)
    elif suffix == ".txt":
        from langchain_community.document_loaders import TextLoader

        loader = TextLoader(file_path, encoding="utf-8")
    else:
        from langchain_community.document_loaders import UnstructuredFileLoader

        loader = UnstructuredFileLoader(file_path)

    return loader.load()


def _build_splitter(
    section_based: bool, chunk_size: int, chunk_overlap: int
) -> RecursiveCharacterTextSplitter:
    if section_based:
        return RecursiveCharacterTextSplitter(
            separators=["\n\n", "\n"],
            chunk_size=10_000,
            chunk_overlap=0,
        )
    return RecursiveCharacterTextSplitter(chunk_size=chunk_size, chunk_overlap=chunk_overlap)


def _annotate_chunks(chunks: list[Document], document_id: str, filename: str = "") -> None:
    for i, chunk in enumerate(chunks):
        chunk.metadata["document_id"] = document_id
        chunk.metadata["chunk_index"] = i
        if filename:
            chunk.metadata["filename"] = filename


async def ingest_from_text(
    text: str,
    backend: StorageBackend,
    filename: str = "",
    chunk_size: int = 800,
    chunk_overlap: int = 100,
    section_based: bool = False,
    document_id: str | None = None,
) -> tuple[int, str]:
    if document_id is None:
        document_id = str(uuid.uuid4())

    splitter = _build_splitter(section_based, chunk_size, chunk_overlap)
    chunks = splitter.split_documents([Document(page_content=text, metadata={})])
    _annotate_chunks(chunks, document_id, filename)

    chunk_count = await backend.ingest(document_id, filename, chunks)
    return chunk_count, document_id


async def ingest_from_file(
    file_path: str,
    filename: str,
    backend: StorageBackend,
    chunk_size: int = 800,
    chunk_overlap: int = 100,
    section_based: bool = False,
    document_id: str | None = None,
) -> tuple[int, str]:
    if document_id is None:
        document_id = str(uuid.uuid4())

    splitter = _build_splitter(section_based, chunk_size, chunk_overlap)
    chunks = splitter.split_documents(load_documents(file_path, filename))
    _annotate_chunks(chunks, document_id, filename)

    chunk_count = await backend.ingest(document_id, filename, chunks)
    return chunk_count, document_id
