from pathlib import Path
from typing import Annotated

from motor.motor_asyncio import AsyncIOMotorDatabase
from fastapi import APIRouter, Depends, File, Form, HTTPException, UploadFile
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.config import settings
from app.core.ingestion import ingest_file
from app.core.retriever_factory import get_database_backend
from app.db.database import get_db
from app.db.mongo import get_mongo_db
from app.db.models import Database, User
from app.dependencies import get_current_user
from app.models.requests import ChunkSettings, DatabaseSettings
from app.models.responses import DocumentListResponse, UploadResponse

router = APIRouter()


async def _get_database_or_404(db_id: str, user_id: str, db: AsyncSession) -> Database:
    result = await db.execute(
        select(Database).where(Database.id == db_id, Database.user_id == user_id)
    )
    database = result.scalar_one_or_none()
    if database is None:
        raise HTTPException(status_code=404, detail="Database not found")
    return database


@router.post("/upload", response_model=list[UploadResponse])
async def upload_documents(
    files: Annotated[list[UploadFile], File()],
    db_id: Annotated[str, Form()],
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
    mongo: AsyncIOMotorDatabase = Depends(get_mongo_db),
):
    database = await _get_database_or_404(db_id, current_user.id, db)
    b = get_database_backend(db_id, database.backend_type, current_user.id)

    doc = await mongo.database_settings.find_one({"db_id": db_id})
    if doc:
        doc.pop("_id", None)
        doc.pop("db_id", None)
        try:
            db_settings = DatabaseSettings(**doc)
        except Exception:
            db_settings = DatabaseSettings()
    else:
        db_settings = DatabaseSettings()

    chunk = db_settings.chunk or ChunkSettings()
    chunk_size = chunk.chunk_size
    chunk_overlap = chunk.chunk_overlap
    section_based = chunk.section_based

    results = []
    for file in files:
        try:
            result = await ingest_file(
                file, b,
                chunk_size=chunk_size,
                chunk_overlap=chunk_overlap,
                section_based=section_based,
            )
            results.append(result)
        except Exception as e:
            raise HTTPException(status_code=500, detail=str(e))
    return results


@router.get("", response_model=list[DocumentListResponse])
async def list_documents(
    db_id: str,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    database = await _get_database_or_404(db_id, current_user.id, db)
    return await get_database_backend(db_id, database.backend_type, current_user.id).list_documents()


@router.delete("/{document_id}")
async def delete_document(
    document_id: str,
    db_id: str,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    database = await _get_database_or_404(db_id, current_user.id, db)
    deleted = await get_database_backend(db_id, database.backend_type, current_user.id).delete_document(document_id)
    if not deleted:
        raise HTTPException(status_code=404, detail="Document not found")
    for f in Path(settings.upload_dir).glob(f"{document_id}.*"):
        f.unlink(missing_ok=True)
    return {"deleted": True, "document_id": document_id}
