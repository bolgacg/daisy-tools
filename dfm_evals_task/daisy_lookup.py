"""DAISY with one Wikipedia lookup, as an Inspect AI task in the dfm-evals format.

Same dataset, prompt, decoding and scorer as dfm_evals.tasks.daisy. The one change is a lookup before the
model answers: the question is sent, as it is, to a BM25 index over the Danish Wikipedia dump of
1 November 2023 (built by scripts/build_localwiki.py), the introductions of the top three pages are put in
front of their prompt, and the model answers as before. No model writes a query and no field of the
benchmark other than the question is used.

Tasks
  daisy_lookup   main line: one plain lookup with the question as the query
  daisy_tool     the model decides: the same lookup offered as a native tool call, answering directly is allowed

Run (any OpenAI-compatible server, for example llama-server on port 8080):
  OPENAI_API_KEY=none inspect eval dfm_evals_task/daisy_lookup.py@daisy_lookup \
      --model openai/gemma4b --model-base-url http://127.0.0.1:8080/v1
Task arguments: -T index_path=/path/to/dawiki.sqlite -T k=3 -T chars=900
"""
from __future__ import annotations

import sys
import threading
from pathlib import Path

from inspect_ai import Task, task
from inspect_ai.dataset import hf_dataset
from inspect_ai.solver import Generate, Solver, TaskState, generate, solver, use_tools
from inspect_ai.tool import tool

HERE = Path(__file__).resolve().parent
ROOT = HERE.parent
for p in (str(HERE), str(ROOT)):
    if p not in sys.path:
        sys.path.insert(0, p)

try:  # the installed dfm-evals wins; otherwise the vendored copy of their task file
    from dfm_evals.tasks.daisy import (  # type: ignore
        DEFAULT_HUGGING_FACE_ID, DEFAULT_MAX_GEN_TOKS, DEFAULT_PROMPT_TEMPLATE, DEFAULT_QUESTION_FIELD,
        DEFAULT_SPLIT, DEFAULT_TARGET_FIELD, DEFAULT_TEMPERATURE, daisy_scorer, normalize_text, record_to_sample)
except ImportError:
    from _upstream_daisy import (  # type: ignore
        DEFAULT_HUGGING_FACE_ID, DEFAULT_MAX_GEN_TOKS, DEFAULT_PROMPT_TEMPLATE, DEFAULT_QUESTION_FIELD,
        DEFAULT_SPLIT, DEFAULT_TARGET_FIELD, DEFAULT_TEMPERATURE, daisy_scorer, normalize_text, record_to_sample)

from daisy_tools import localwiki, query  # noqa: E402  (repo root on sys.path above)

query.search, query.extracts = localwiki.search, localwiki.extracts  # the offline index behind the rule query

CONTEXT_HEADER = "Baggrundsviden fra dansk Wikipedia:\n"
TOOL_DESCRIPTION = "Søg i dansk Wikipedia og få de første afsnit af de bedste artikler."


def set_index(index_path: str | None) -> None:
    if index_path:
        localwiki.DB = str(Path(index_path).expanduser())
        localwiki._local = threading.local()
    if not Path(localwiki.DB).exists():
        raise FileNotFoundError(f"offline index not found at {localwiki.DB}; build it with scripts/build_localwiki.py "
                                f"or pass -T index_path=...")


def ctx_block(docs, chars: int) -> str:
    parts = []
    for title, text in docs:
        text = (text or "").strip().replace("\n", " ")
        parts.append(f"[{title}] {text[:chars]}")
    return "\n".join(parts)


@solver
def prepend_lookup(k: int = 3, chars: int = 900) -> Solver:
    """One lookup, the question itself as the query, top-k page introductions in front of the prompt."""

    async def solve(state: TaskState, generate: Generate) -> TaskState:
        question = state.metadata["question"]
        docs, used = query.shaped_lookup(question, limit=k, chars=chars)
        block = ctx_block(docs, chars)
        state.user_prompt.text = CONTEXT_HEADER + block + "\n\n" + state.user_prompt.text
        answer = state.metadata.get("answer") or ""
        state.metadata["tool_query"] = used
        state.metadata["titles"] = [t for t, _ in docs]
        state.metadata["ctx_has_gold"] = bool(answer) and normalize_text(answer) in normalize_text(block)
        return state

    return solve


@tool
def search_wikipedia(k: int = 3, chars: int = 900):
    async def execute(query: str) -> str:
        """Søg i dansk Wikipedia og få de første afsnit af de bedste artikler.

        Args:
            query: søgeord
        """
        docs = localwiki.lookup(query, limit=k, chars=chars)
        return ctx_block(docs, chars) or "Ingen resultater."

    return execute


def _dataset(hugging_face_id, split, prompt_template, question_field, target_field, shuffle, seed, limit):
    return hf_dataset(
        path=hugging_face_id,
        split=split.strip(),
        sample_fields=lambda record: record_to_sample(
            record=record, prompt_template=prompt_template,
            question_field=question_field, target_field=target_field),
        auto_id=True, shuffle=shuffle, seed=seed, limit=limit)


@task(name="daisy_lookup")
def daisy_lookup(
    index_path: str | None = None,
    k: int = 3,
    chars: int = 900,
    hugging_face_id: str = DEFAULT_HUGGING_FACE_ID,
    split: str = DEFAULT_SPLIT,
    prompt_template: str = DEFAULT_PROMPT_TEMPLATE,
    question_field: str = DEFAULT_QUESTION_FIELD,
    target_field: str = DEFAULT_TARGET_FIELD,
    max_gen_toks: int = DEFAULT_MAX_GEN_TOKS,
    temperature: float = DEFAULT_TEMPERATURE,
    shuffle: bool = False,
    seed: int | None = None,
    limit: int | None = None,
) -> Task:
    set_index(index_path)
    return Task(
        dataset=_dataset(hugging_face_id, split, prompt_template, question_field, target_field, shuffle, seed, limit),
        solver=[prepend_lookup(k=k, chars=chars), generate(max_tokens=max_gen_toks, temperature=temperature)],
        scorer=[daisy_scorer()],
    )


@task(name="daisy_tool")
def daisy_tool(
    index_path: str | None = None,
    k: int = 3,
    chars: int = 900,
    hugging_face_id: str = DEFAULT_HUGGING_FACE_ID,
    split: str = DEFAULT_SPLIT,
    prompt_template: str = DEFAULT_PROMPT_TEMPLATE,
    question_field: str = DEFAULT_QUESTION_FIELD,
    target_field: str = DEFAULT_TARGET_FIELD,
    max_gen_toks: int = DEFAULT_MAX_GEN_TOKS,
    temperature: float = DEFAULT_TEMPERATURE,
    shuffle: bool = False,
    seed: int | None = None,
    limit: int | None = None,
) -> Task:
    set_index(index_path)
    return Task(
        dataset=_dataset(hugging_face_id, split, prompt_template, question_field, target_field, shuffle, seed, limit),
        solver=[use_tools(search_wikipedia(k=k, chars=chars)), generate(max_tokens=max_gen_toks, temperature=temperature)],
        scorer=[daisy_scorer()],
    )
