from langchain_core.documents import Document

from rag_backends.qa_chain import build_chain as _build_chain
from app.config import settings
from app.models.responses import SourceDocument


def build_chain(retriever, llm_model: str | None = None):
    model = llm_model or settings.llm_model
    return _build_chain(retriever, llm_model=model, openai_api_key=settings.openai_api_key)


def format_sources(docs: list[Document]) -> list[SourceDocument]:
    return [
        SourceDocument(
            document_id=doc.metadata.get("document_id", ""),
            filename=doc.metadata.get("filename", ""),
            content_preview=doc.page_content[:200],
            score=doc.metadata.get("score"),
        )
        for doc in docs
    ]
