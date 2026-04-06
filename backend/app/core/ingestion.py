import os
import uuid

from fastapi import UploadFile

from rag_backends.base import StorageBackend
from rag_backends.ingestion import ingest_from_file as _ingest_from_file
from app.config import settings
from app.models.responses import UploadResponse
from app.utils.file_utils import save_upload


async def ingest_file(upload: UploadFile, backend: StorageBackend) -> UploadResponse:
    document_id = str(uuid.uuid4())
    filename = upload.filename or "unknown"
    file_path = await save_upload(upload, settings.upload_dir, document_id)

    try:
        chunk_count = await _ingest_from_file(file_path, filename, document_id, backend)
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
