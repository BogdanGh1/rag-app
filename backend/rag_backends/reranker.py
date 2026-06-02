import json

from langchain_core.documents import Document
from langchain_openai import ChatOpenAI

_SYSTEM_PROMPT = """\
You are a relevance-grading assistant. Given a question and a list of text chunks, \
identify which chunks contain information useful for answering the question.

Respond with a JSON object with a single key "relevant_indices" whose value is an \
array of the zero-based indices of the chunks that are relevant. If none are relevant, \
return an empty array."""


def rerank(
    docs: list[Document],
    question: str,
    llm_model: str,
    openai_api_key: str,
) -> list[Document]:
    if not docs:
        return docs

    numbered = "\n\n".join(
        f"[{i}] {doc.page_content}" for i, doc in enumerate(docs)
    )
    user_message = f"Question: {question}\n\nChunks:\n{numbered}"

    llm = ChatOpenAI(model=llm_model, temperature=0, api_key=openai_api_key)
    response = llm.invoke(
        [
            {"role": "system", "content": _SYSTEM_PROMPT},
            {"role": "user", "content": user_message},
        ],
        response_format={"type": "json_object"},
    )

    try:
        parsed = json.loads(response.content)
        indices = parsed.get("relevant_indices", [])
        return [docs[i] for i in indices if isinstance(i, int) and 0 <= i < len(docs)]
    except (json.JSONDecodeError, KeyError):
        return docs
