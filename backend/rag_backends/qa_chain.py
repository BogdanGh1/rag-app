from langchain_core.documents import Document
from langchain_core.output_parsers import StrOutputParser
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.retrievers import BaseRetriever
from langchain_core.runnables import RunnableParallel, RunnablePassthrough
from langchain_openai import ChatOpenAI

_PROMPT_TEMPLATE = """\
You are a helpful assistant that answers questions based on the provided context.
If the context does not contain enough information to answer the question, say \
"I don't have enough information to answer this question based on the provided documents."

Context:
{context}

Question: {question}

Answer:"""


def _format_docs(docs: list[Document]) -> str:
    return "\n\n".join(doc.page_content for doc in docs)


def build_chain(retriever: BaseRetriever, llm_model: str, openai_api_key: str):
    """Return a chain that takes a question string and returns
    {"context": [Document, ...], "question": str, "answer": str}."""
    llm = ChatOpenAI(model=llm_model, temperature=0, api_key=openai_api_key)
    prompt = ChatPromptTemplate.from_template(_PROMPT_TEMPLATE)

    rag_chain_from_docs = (
        RunnablePassthrough.assign(context=lambda x: _format_docs(x["context"]))
        | prompt
        | llm
        | StrOutputParser()
    )

    return RunnableParallel(
        context=retriever,
        question=RunnablePassthrough(),
    ).assign(answer=rag_chain_from_docs)
