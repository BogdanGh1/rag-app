import json
from concurrent.futures import ThreadPoolExecutor, as_completed
from dataclasses import dataclass

from langchain_core.output_parsers import StrOutputParser
from langchain_core.prompts import ChatPromptTemplate
from langchain_openai import ChatOpenAI

_EVAL_PROMPT = """\
You are an evaluation judge. Your task is to decide whether a generated answer \
conveys the same meaning as the expected answer.

Generated answer:
{generated}

Expected answer:
{expected}

Reply with a JSON object and nothing else:
{{"similar": true|false, "reason": "<one sentence explanation>"}}"""


@dataclass
class EvalResult:
    similar: bool
    reason: str


def evaluate_answer(
    generated: str,
    expected: str,
    llm_model: str,
    openai_api_key: str,
) -> EvalResult:
    """Use an LLM to judge whether *generated* is semantically similar to *expected*."""
    llm = ChatOpenAI(model=llm_model, temperature=0, api_key=openai_api_key)
    prompt = ChatPromptTemplate.from_template(_EVAL_PROMPT)
    chain = prompt | llm | StrOutputParser()

    raw = chain.invoke({"generated": generated, "expected": expected})

    try:
        data = json.loads(raw)
        return EvalResult(similar=bool(data["similar"]), reason=str(data["reason"]))
    except (json.JSONDecodeError, KeyError):
        return EvalResult(similar=False, reason=f"Could not parse LLM response: {raw}")


def evaluate_answers(
    pairs: list[tuple[str, str]],
    llm_model: str,
    openai_api_key: str,
    max_workers: int = 8,
) -> list[EvalResult]:
    """Evaluate multiple (generated, expected) pairs in parallel using threads.

    Returns results in the same order as *pairs*.
    """
    results: list[EvalResult | None] = [None] * len(pairs)

    with ThreadPoolExecutor(max_workers=max_workers) as executor:
        futures = {
            executor.submit(evaluate_answer, gen, exp, llm_model, openai_api_key): i
            for i, (gen, exp) in enumerate(pairs)
        }
        for future in as_completed(futures):
            results[futures[future]] = future.result()

    return results  # type: ignore[return-value]
