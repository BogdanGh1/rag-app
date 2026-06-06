"""From-scratch RAG evaluation metrics (ragas-style, no ragas dependency).

Metrics implemented:

* **Faithfulness** (LLM judge, context-based): fraction of the atomic claims in the
  generated answer that can be inferred from the retrieved context. Measures
  hallucination.
* **Answer relevance** (LLM judge): how directly and completely the answer responds
  to the question, ignoring factual correctness.
* **Answer similarity** (LLM judge, kept from the original module): whether the
  generated answer conveys the same meaning as the expected/ground-truth answer.
* **Context precision** (filename-based): rank-weighted precision of the retrieved
  chunks, where a chunk is "relevant" if its filename matches the expected filename.
* **Reciprocal rank** (filename-based): 1/r where r is the rank of the first retrieved
  chunk matching the expected filename, or 0.0 if none matches. Averaging this over a
  batch of questions gives the mean reciprocal rank (MRR), which captures *where* the
  relevant content is ranked rather than merely how much of the set is relevant.

The pipeline (`build_eval_chain` + `evaluate_question`) builds a QA chain from a
backend, runs a question through it, and scores every metric in one `QuestionEval`.
"""

import json
import pickle
from concurrent.futures import ThreadPoolExecutor
from dataclasses import dataclass, field
from pathlib import Path

from langchain_core.documents import Document
from langchain_core.output_parsers import StrOutputParser
from langchain_core.prompts import ChatPromptTemplate
from langchain_openai import ChatOpenAI

from rag_backends.qa_chain import build_chain

# --------------------------------------------------------------------------- #
# Prompts
# --------------------------------------------------------------------------- #

_SIMILAR_PROMPT = """\
You are an evaluation judge. Your task is to decide whether a generated answer \
conveys the same meaning as the expected answer.

Generated answer:
{generated}

Expected answer:
{expected}

Reply with a JSON object and nothing else:
{{"similar": true|false, "reason": "<one sentence explanation>"}}"""

_FAITHFULNESS_PROMPT = """\
You are an evaluation judge measuring the faithfulness of an answer to its context.
Break the answer into atomic factual claims. For each claim decide whether it can be \
directly inferred from the context. Do not use any outside knowledge.

Context:
{context}

Answer:
{answer}

Reply with a JSON object and nothing else:
{{"claims": [{{"claim": "<text>", "supported": true|false}}, ...]}}
If the answer makes no factual claims (for example it says it cannot answer), \
return {{"claims": []}}."""

_RELEVANCE_PROMPT = """\
You are an evaluation judge measuring how well an answer addresses a question.
Score from 0.0 to 1.0 how directly and completely the answer responds to the question, \
ignoring whether it is factually correct. An answer that is evasive, off-topic, \
incomplete, or states that it cannot answer should score low.

Question:
{question}

Answer:
{answer}

Reply with a JSON object and nothing else:
{{"relevance": <float between 0.0 and 1.0>, "reason": "<one sentence explanation>"}}"""


# --------------------------------------------------------------------------- #
# Result types
# --------------------------------------------------------------------------- #


@dataclass
class EvalResult:
    """Result of the answer-similarity judge (vs. the expected answer)."""

    similar: bool
    reason: str


@dataclass
class QuestionEval:
    """All metrics for a single evaluated question."""

    question: str
    answer: str
    expected_answer: str
    faithfulness: float
    answer_relevance: float
    answer_relevance_reason: str
    similar: bool
    similar_reason: str
    context_precision: float
    reciprocal_rank: float
    retrieved_filenames: list[str] = field(default_factory=list)
    expected_filename: str = ""

    def __repr__(self) -> str:
        return (
            "QuestionEval(\n"
            f"  question={self.question!r},\n"
            f"  answer={self.answer!r},\n"
            f"  expected_answer={self.expected_answer!r},\n"
            f"  faithfulness={self.faithfulness:.3f},\n"
            f"  answer_relevance={self.answer_relevance:.3f},\n"
            f"  answer_relevance_reason={self.answer_relevance_reason!r},\n"
            f"  similar={self.similar},\n"
            f"  similar_reason={self.similar_reason!r},\n"
            f"  context_precision={self.context_precision:.3f},\n"
            f"  reciprocal_rank={self.reciprocal_rank:.3f},\n"
            f"  retrieved_filenames={self.retrieved_filenames},\n"
            f"  expected_filename={self.expected_filename!r}\n"
            ")"
        )


# --------------------------------------------------------------------------- #
# Helpers
# --------------------------------------------------------------------------- #


def _make_llm(llm_model: str, openai_api_key: str) -> ChatOpenAI:
    return ChatOpenAI(model=llm_model, temperature=0, api_key=openai_api_key)


def _judge(llm: ChatOpenAI, template: str, values: dict) -> str:
    chain = ChatPromptTemplate.from_template(template) | llm | StrOutputParser()
    return chain.invoke(values)


def _parse_json(raw: str) -> dict | None:
    try:
        return json.loads(raw)
    except json.JSONDecodeError:
        # Tolerate models that wrap JSON in ```json fences or add stray prose.
        start, end = raw.find("{"), raw.rfind("}")
        if start != -1 and end > start:
            try:
                return json.loads(raw[start : end + 1])
            except json.JSONDecodeError:
                return None
        return None


def _doc_filenames(docs: list[Document]) -> list[str]:
    return [doc.metadata.get("filename", "") for doc in docs]


# --------------------------------------------------------------------------- #
# Metric: answer similarity (vs. expected answer) — kept from original module
# --------------------------------------------------------------------------- #


def evaluate_answer(
    generated: str,
    expected: str,
    llm_model: str,
    openai_api_key: str,
) -> EvalResult:
    """Use an LLM to judge whether *generated* is semantically similar to *expected*."""
    return _evaluate_answer(generated, expected, _make_llm(llm_model, openai_api_key))


def _evaluate_answer(generated: str, expected: str, llm: ChatOpenAI) -> EvalResult:
    raw = _judge(llm, _SIMILAR_PROMPT, {"generated": generated, "expected": expected})
    data = _parse_json(raw)
    if data is None or "similar" not in data:
        return EvalResult(similar=False, reason=f"Could not parse LLM response: {raw}")
    return EvalResult(similar=bool(data["similar"]), reason=str(data.get("reason", "")))


def evaluate_answers(
    pairs: list[tuple[str, str]],
    llm_model: str,
    openai_api_key: str,
    max_workers: int = 8,
) -> list[EvalResult]:
    """Judge a batch of (generated, expected) pairs in parallel, preserving order."""
    llm = _make_llm(llm_model, openai_api_key)
    with ThreadPoolExecutor(max_workers=max_workers) as executor:
        return list(
            executor.map(lambda p: _evaluate_answer(p[0], p[1], llm), pairs)
        )


# --------------------------------------------------------------------------- #
# Metric: faithfulness (LLM judge, context-based)
# --------------------------------------------------------------------------- #


def evaluate_faithfulness(answer: str, context_docs: list[Document], llm: ChatOpenAI) -> float:
    """Fraction of the answer's atomic claims that are supported by the context.

    An answer that makes no factual claims (e.g. "I cannot answer") contradicts
    nothing in the context, so it is treated as trivially faithful (1.0).
    """
    context = "\n\n".join(doc.page_content for doc in context_docs)
    raw = _judge(llm, _FAITHFULNESS_PROMPT, {"context": context, "answer": answer})
    data = _parse_json(raw)
    if data is None or "claims" not in data:
        return 0.0

    claims = data["claims"] or []
    if not claims:
        return 1.0

    supported = sum(1 for c in claims if bool(c.get("supported")))
    return supported / len(claims)


# --------------------------------------------------------------------------- #
# Metric: answer relevance (LLM judge)
# --------------------------------------------------------------------------- #


def evaluate_answer_relevance(question: str, answer: str, llm: ChatOpenAI) -> tuple[float, str]:
    """LLM-judged score (0..1) of how well the answer addresses the question."""
    raw = _judge(llm, _RELEVANCE_PROMPT, {"question": question, "answer": answer})
    data = _parse_json(raw)
    if data is None or "relevance" not in data:
        return 0.0, f"Could not parse LLM response: {raw}"
    try:
        score = max(0.0, min(1.0, float(data["relevance"])))
    except (TypeError, ValueError):
        return 0.0, f"Non-numeric relevance score: {raw}"
    return score, str(data.get("reason", ""))


# --------------------------------------------------------------------------- #
# Metric: context precision (filename-based, no LLM)
# --------------------------------------------------------------------------- #


def context_precision(retrieved_filenames: list[str], expected_filename: str) -> float:
    """Rank-weighted precision of the retrieved chunks (ragas-style).

    A retrieved chunk is relevant when its filename equals *expected_filename*.
    Score = mean of Precision@k over the ranks where a relevant chunk appears.
    Returns 0.0 when nothing relevant was retrieved.
    """
    if not retrieved_filenames or not expected_filename:
        return 0.0

    hits = 0
    weighted = 0.0
    for k, name in enumerate(retrieved_filenames, start=1):
        if name == expected_filename:
            hits += 1
            weighted += hits / k  # Precision@k at this relevant rank
    if hits == 0:
        return 0.0
    return weighted / hits


def reciprocal_rank(retrieved_filenames: list[str], expected_filename: str) -> float:
    """Reciprocal rank of the first chunk matching *expected_filename*.

    Returns 1/r where r is the (1-based) position of the highest-ranked retrieved
    chunk whose filename equals *expected_filename*, or 0.0 if none matches.
    Averaged over a batch of questions this yields the mean reciprocal rank (MRR).
    """
    if not expected_filename:
        return 0.0
    for r, name in enumerate(retrieved_filenames, start=1):
        if name == expected_filename:
            return 1.0 / r
    return 0.0


def mean_reciprocal_rank(evals: list["QuestionEval"]) -> float:
    """Mean reciprocal rank (MRR) over a batch of evaluated questions."""
    if not evals:
        return 0.0
    return sum(e.reciprocal_rank for e in evals) / len(evals)


# --------------------------------------------------------------------------- #
# Pipeline
# --------------------------------------------------------------------------- #


def build_eval_chain(backend, llm_model: str, openai_api_key: str, top_k: int = 5):
    """Build a QA chain from a backend, ready to be passed to `evaluate_question`."""
    retriever = backend.get_retriever(top_k=top_k)
    return build_chain(retriever, llm_model=llm_model, openai_api_key=openai_api_key)


def evaluate_question(
    question: str,
    expected_answer: str,
    expected_filename: str,
    chain,
    llm_model: str,
    openai_api_key: str,
    cache_dir: str | None = None,
) -> QuestionEval:
    """Run *question* through *chain* and score every metric into a `QuestionEval`.

    *chain* is a chain built by `build_eval_chain` (or `build_chain`); invoking it
    with a question string returns ``{"context": [Document, ...], "question", "answer"}``.

    If *cache_dir* is given, the result is pickled to ``{cache_dir}/{expected_filename}.pk``.
    A cached file is loaded and returned instead of re-running the (LLM-backed) evaluation.
    """
    cache_path = (
        Path(cache_dir) / f"{expected_filename}.pk" if cache_dir else None
    )
    if cache_path is not None and cache_path.exists():
        with cache_path.open("rb") as f:
            return pickle.load(f)

    result = chain.invoke(question)
    context_docs: list[Document] = result["context"]
    answer: str = result["answer"]

    llm = _make_llm(llm_model, openai_api_key)
    retrieved = _doc_filenames(context_docs)

    faithfulness = evaluate_faithfulness(answer, context_docs, llm)
    relevance, relevance_reason = evaluate_answer_relevance(question, answer, llm)
    similar = _evaluate_answer(answer, expected_answer, llm)

    question_eval = QuestionEval(
        question=question,
        answer=answer,
        expected_answer=expected_answer,
        faithfulness=faithfulness,
        answer_relevance=relevance,
        answer_relevance_reason=relevance_reason,
        similar=similar.similar,
        similar_reason=similar.reason,
        context_precision=context_precision(retrieved, expected_filename),
        reciprocal_rank=reciprocal_rank(retrieved, expected_filename),
        retrieved_filenames=retrieved,
        expected_filename=expected_filename,
    )

    if cache_path is not None:
        cache_path.parent.mkdir(parents=True, exist_ok=True)
        with cache_path.open("wb") as f:
            pickle.dump(question_eval, f)

    return question_eval


def evaluate_questions(
    items: list[tuple[str, str, str]],
    chain,
    llm_model: str,
    openai_api_key: str,
    max_workers: int = 12,
    cache_dir: str | None = None,
) -> list[QuestionEval]:
    """Evaluate a batch of (question, expected_answer, expected_filename) in parallel.

    Order is preserved. Each item runs the chain and all metrics independently.
    If *cache_dir* is given, each result is cached to ``{cache_dir}/{expected_filename}.pk``
    and reused on subsequent runs (see `evaluate_question`).
    """
    with ThreadPoolExecutor(max_workers=max_workers) as executor:
        return list(
            executor.map(
                lambda it: evaluate_question(
                    it[0], it[1], it[2], chain, llm_model, openai_api_key, cache_dir
                ),
                items,
            )
        )
