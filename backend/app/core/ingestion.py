import os
import uuid
from pathlib import Path

from fastapi import UploadFile
from langchain_core.documents import Document
from langchain_text_splitters import RecursiveCharacterTextSplitter

from app.backends.base import StorageBackend
from app.config import settings
from app.models.responses import UploadResponse
from app.utils.file_utils import save_upload

_SPLITTER = RecursiveCharacterTextSplitter(chunk_size=800, chunk_overlap=100)


def _load_documents(file_path: str, filename: str) -> list[Document]:
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


async def ingest_file(upload: UploadFile, backend: StorageBackend) -> UploadResponse:
    document_id = str(uuid.uuid4())
    filename = upload.filename or "unknown"
    file_path = await save_upload(upload, settings.upload_dir, document_id)

    try:
        raw_docs = _load_documents(file_path, filename)
        chunks = _SPLITTER.split_documents(raw_docs)

        for i, chunk in enumerate(chunks):
            chunk.metadata["document_id"] = document_id
            chunk.metadata["chunk_index"] = i
            chunk.metadata["filename"] = filename

        chunk_count = await backend.ingest(document_id, filename, chunks)

        return UploadResponse(
            document_id=document_id,
            filename=filename,
            chunk_count=chunk_count,
            backend=backend.name,
        )
    except Exception:
        if os.path.exists(file_path):
            os.remove(file_path)
        raise
