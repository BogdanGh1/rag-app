from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.retriever_factory import BACKEND_NAMES, evict_database_backend
from app.db.database import get_db
from app.db.models import Database, User
from app.dependencies import get_current_user
from app.models.requests import CreateDatabaseRequest
from app.models.responses import DatabaseResponse

router = APIRouter()


@router.post("", response_model=DatabaseResponse, status_code=201)
async def create_database(
    request: CreateDatabaseRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    if request.backend_type not in BACKEND_NAMES:
        raise HTTPException(
            status_code=400,
            detail=f"Unknown backend type {request.backend_type!r}. Available: {BACKEND_NAMES}",
        )
    if not request.name.strip():
        raise HTTPException(status_code=400, detail="Database name cannot be empty")

    database = Database(
        user_id=current_user.id,
        name=request.name.strip(),
        backend_type=request.backend_type,
    )
    db.add(database)
    try:
        await db.commit()
        await db.refresh(database)
    except IntegrityError:
        await db.rollback()
        raise HTTPException(
            status_code=409, detail=f"A database named {request.name!r} already exists"
        )

    return DatabaseResponse(
        id=database.id,
        name=database.name,
        backend_type=database.backend_type,
        created_at=database.created_at,
    )


@router.get("", response_model=list[DatabaseResponse])
async def list_databases(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(
        select(Database).where(Database.user_id == current_user.id).order_by(Database.created_at)
    )
    databases = result.scalars().all()
    return [
        DatabaseResponse(
            id=d.id,
            name=d.name,
            backend_type=d.backend_type,
            created_at=d.created_at,
        )
        for d in databases
    ]


@router.delete("/{db_id}", status_code=204)
async def delete_database(
    db_id: str,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(
        select(Database).where(Database.id == db_id, Database.user_id == current_user.id)
    )
    database = result.scalar_one_or_none()
    if database is None:
        raise HTTPException(status_code=404, detail="Database not found")

    await db.delete(database)
    await db.commit()
    evict_database_backend(db_id, current_user.id)
