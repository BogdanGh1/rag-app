from typing import Annotated

from fastapi import APIRouter, File, Form, HTTPException, UploadFile

from app.core.ingestion import ingest_file
from app.core.retriever_factory import get_backend
from app.models.responses import DocumentListResponse, UploadResponse

router = APIRouter()


@router.post("/upload", response_model=list[UploadResponse])
async def upload_documents(
    files: Annotated[list[UploadFile], File()],
    backend: Annotated[str, Form()],
):
    b = get_backend(backend)
    results = []
    for file in files:
        try:
            result = await ingest_file(file, b)
            results.append(result)
        except Exception as e:
            raise HTTPException(status_code=500, detail=str(e))
    return results


@router.get("", response_model=list[DocumentListResponse])
async def list_documents(backend: str):
    return await get_backend(backend).list_documents()


@router.delete("/{document_id}")
async def delete_document(document_id: str, backend: str):
    deleted = await get_backend(backend).delete_document(document_id)
    if not deleted:
        raise HTTPException(status_code=404, detail="Document not found")
    return {"deleted": True, "document_id": document_id}
