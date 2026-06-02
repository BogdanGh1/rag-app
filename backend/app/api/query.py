import json
import time

from fastapi import APIRouter, Depends, HTTPException
from openai import AsyncOpenAI
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.config import settings
from app.core.qa_chain import answer_from_docs, build_chain, format_sources
from app.core.reranker import rerank_docs
from app.core.retriever_factory import get_database_backend
from app.db.database import get_db
from app.db.models import Database, User
from app.dependencies import get_current_user
from app.models.requests import QueryRequest, SmartQueryRequest
from app.models.responses import QueryResponse, RoutedDatabase, SmartQueryResponse

router = APIRouter()


async def _rewrite_question(question: str, llm_model: str | None) -> str:
    client = AsyncOpenAI(api_key=settings.openai_api_key)
    model = llm_model or settings.llm_model
    response = await client.chat.completions.create(
        model=model,
        messages=[
            {
                "role": "system",
                "content": (
                    "You are a query-rewriting assistant. "
                    "Rewrite the user's question to be clearer, more specific, and better suited for document retrieval. "
                    "Return only the rewritten question with no preamble or explanation."
                ),
            },
            {"role": "user", "content": question},
        ],
        temperature=0,
    )
    return response.choices[0].message.content.strip()


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
        rewritten_question = None
        if request.rewrite_question:
            rewritten_question = await _rewrite_question(request.question, request.llm_model)

        active_question = rewritten_question or request.question

        backend = get_database_backend(request.db_id, database.backend_type, current_user.id)
        retriever = backend.get_retriever(top_k=request.top_k)

        start = time.time()

        if request.rerank:
            docs = retriever.invoke(active_question)
            docs = rerank_docs(docs, active_question, llm_model=request.llm_model)
            answer = answer_from_docs(docs, active_question, llm_model=request.llm_model)
            context = docs
        else:
            chain = build_chain(retriever, llm_model=request.llm_model)
            chain_result = chain.invoke(active_question)
            answer = chain_result["answer"]
            context = chain_result["context"]

        latency_ms = int((time.time() - start) * 1000)

        return QueryResponse(
            question=request.question,
            rewritten_question=rewritten_question,
            answer=answer,
            sources=format_sources(context),
            backend_used=database.backend_type,
            latency_ms=latency_ms,
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


async def _route_question(
    question: str,
    databases: list[Database],
    llm_model: str | None,
) -> tuple[list[str], str]:
    client = AsyncOpenAI(api_key=settings.openai_api_key)
    model = llm_model or settings.llm_model

    db_list = "\n".join(
        f"- ID: {db.id}, Name: {db.name}, Description: {db.description or 'No description provided'}"
        for db in databases
    )

    prompt = f"""You are a routing assistant. Given a user question and a list of knowledge-base databases, select the database(s) most likely to contain relevant information.

Available databases:
{db_list}

User question: {question}

Respond with a JSON object:
- "selected_ids": array of database IDs to query (include multiple if the question spans topics)
- "explanation": one sentence explaining which databases were chosen and why

Only select databases that are genuinely relevant. Return an empty array if none apply."""

    response = await client.chat.completions.create(
        model=model,
        messages=[{"role": "user", "content": prompt}],
        response_format={"type": "json_object"},
        temperature=0,
    )

    parsed = json.loads(response.choices[0].message.content)
    return parsed.get("selected_ids", []), parsed.get("explanation", "")


@router.post("/query/smart", response_model=SmartQueryResponse)
async def smart_query(
    request: SmartQueryRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(
        select(Database).where(Database.user_id == current_user.id)
    )
    all_databases = result.scalars().all()

    if not all_databases:
        raise HTTPException(status_code=404, detail="No databases found. Create a database first.")

    try:
        selected_ids, explanation = await _route_question(
            request.question, all_databases, request.llm_model
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Routing failed: {e}")

    routed = [db for db in all_databases if db.id in set(selected_ids)]

    if not routed:
        raise HTTPException(
            status_code=422,
            detail="No suitable database found for this question. Try adding relevant documents or rephrasing.",
        )

    try:
        rewritten_question = None
        if request.rewrite_question:
            rewritten_question = await _rewrite_question(request.question, request.llm_model)

        active_question = rewritten_question or request.question

        start = time.time()
        all_docs = []
        for database in routed:
            backend = get_database_backend(database.id, database.backend_type, current_user.id)
            retriever = backend.get_retriever(top_k=request.top_k)
            docs = retriever.invoke(active_question)
            all_docs.extend(docs)

        if request.rerank:
            all_docs = rerank_docs(all_docs, active_question, llm_model=request.llm_model)

        answer = answer_from_docs(all_docs, active_question, llm_model=request.llm_model)
        latency_ms = int((time.time() - start) * 1000)

        return SmartQueryResponse(
            question=request.question,
            rewritten_question=rewritten_question,
            answer=answer,
            sources=format_sources(all_docs),
            routed_databases=[
                RoutedDatabase(id=db.id, name=db.name, description=db.description)
                for db in routed
            ],
            routing_explanation=explanation,
            latency_ms=latency_ms,
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
