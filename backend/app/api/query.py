import time

from fastapi import APIRouter, Depends, HTTPException

from app.core.qa_chain import build_chain, format_sources
from app.core.retriever_factory import get_user_backend
from app.db.models import User
from app.dependencies import get_current_user
from app.models.requests import QueryRequest
from app.models.responses import QueryResponse

router = APIRouter()


@router.post("/query", response_model=QueryResponse)
async def query_documents(
    request: QueryRequest,
    current_user: User = Depends(get_current_user),
):
    try:
        backend = get_user_backend(request.backend, current_user.id)
        retriever = backend.get_retriever(top_k=request.top_k)
        chain = build_chain(retriever, llm_model=request.llm_model)

        start = time.time()
        result = chain.invoke(request.question)
        latency_ms = int((time.time() - start) * 1000)

        return QueryResponse(
            question=request.question,
            answer=result["answer"],
            sources=format_sources(result["context"]),
            backend_used=backend.name,
            latency_ms=latency_ms,
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
