from langchain_core.documents import Document

from app.config import settings
from rag_backends.reranker import rerank


def rerank_docs(
    docs: list[Document],
    question: str,
    llm_model: str | None = None,
) -> list[Document]:
    model = llm_model or settings.llm_model
    return rerank(docs, question, llm_model=model, openai_api_key=settings.openai_api_key)
