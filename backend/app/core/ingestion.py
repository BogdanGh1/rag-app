import os

from fastapi import UploadFile

from rag_backends.base import StorageBackend
from rag_backends.ingestion import ingest_from_file
from app.config import settings
from app.models.responses import UploadResponse
from app.utils.file_utils import save_upload


async def ingest_file(
    upload: UploadFile,
    backend: StorageBackend,
    chunk_size: int = 800,
    chunk_overlap: int = 100,
    section_based: bool = False,
) -> UploadResponse:
    filename = upload.filename or "unknown"
    file_path, document_id = await save_upload(upload, settings.upload_dir)

    try:
        chunk_count, document_id = await ingest_from_file(
            file_path, filename, backend, chunk_size, chunk_overlap, section_based,
            document_id=document_id,
        )
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
