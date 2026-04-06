import time

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.qa_chain import build_chain, format_sources
from app.core.retriever_factory import get_database_backend
from app.db.database import get_db
from app.db.models import Database, User
from app.dependencies import get_current_user
from app.models.requests import QueryRequest
from app.models.responses import QueryResponse

router = APIRouter()


@router.post("/query", response_model=QueryResponse)
async def query_documents(
    request: QueryRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(
        select(Database).where(
            Database.id == request.db_id, Database.user_id == current_user.id
        )
    )
    database = result.scalar_one_or_none()
    if database is None:
        raise HTTPException(status_code=404, detail="Database not found")

    try:
        backend = get_database_backend(request.db_id, database.backend_type, current_user.id)
        retriever = backend.get_retriever(top_k=request.top_k)
        chain = build_chain(retriever, llm_model=request.llm_model)

        start = time.time()
        chain_result = chain.invoke(request.question)
        latency_ms = int((time.time() - start) * 1000)

        return QueryResponse(
            question=request.question,
            answer=chain_result["answer"],
            sources=format_sources(chain_result["context"]),
            backend_used=database.backend_type,
            latency_ms=latency_ms,
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
