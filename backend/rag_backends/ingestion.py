from pathlib import Path

from langchain_core.documents import Document
from langchain_text_splitters import RecursiveCharacterTextSplitter

from rag_backends.base import StorageBackend

_SPLITTER = RecursiveCharacterTextSplitter(chunk_size=800, chunk_overlap=100)


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


async def ingest_from_file(
    file_path: str, filename: str, document_id: str, backend: StorageBackend
) -> int:
    raw_docs = load_documents(file_path, filename)
    chunks = _SPLITTER.split_documents(raw_docs)

    for i, chunk in enumerate(chunks):
        chunk.metadata["document_id"] = document_id
        chunk.metadata["chunk_index"] = i
        chunk.metadata["filename"] = filename

    return await backend.ingest(document_id, filename, chunks)
