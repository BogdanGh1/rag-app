from langchain_core.documents import Document
from langchain_core.output_parsers import StrOutputParser
from langchain_core.prompts import ChatPromptTemplate
from langchain_openai import ChatOpenAI

from rag_backends.qa_chain import build_chain as _build_chain
from app.config import settings
from app.models.responses import SourceDocument

_PROMPT_TEMPLATE = """\
You are a helpful assistant that answers questions based on the provided context.
If the context does not contain enough information to answer the question, say \
"I don't have enough information to answer this question based on the provided documents."

Context:
{context}

Question: {question}

Answer:"""


def build_chain(retriever, llm_model: str | None = None):
    model = llm_model or settings.llm_model
    return _build_chain(retriever, llm_model=model, openai_api_key=settings.openai_api_key)


def answer_from_docs(docs: list[Document], question: str, llm_model: str | None = None) -> str:
    model = llm_model or settings.llm_model
    llm = ChatOpenAI(model=model, temperature=0, api_key=settings.openai_api_key)
    prompt = ChatPromptTemplate.from_template(_PROMPT_TEMPLATE)
    chain = prompt | llm | StrOutputParser()
    context = "\n\n".join(doc.page_content for doc in docs)
    return chain.invoke({"context": context, "question": question})


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
