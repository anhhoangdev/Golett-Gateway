from __future__ import annotations

"""
Named-entity extraction that prefers an OpenAI ChatCompletion and
falls back to a naive regex when that isn't possible.

Down-stream usage stays the same::

    from golett_core.memory.retrieval.entity_extraction import extract_entities
"""

import functools
import json
import logging
import os
import re
from collections import OrderedDict
from typing import Dict, Iterable, List, Optional

logger = logging.getLogger(__name__)

# ---------------------------------------------------------------------------#
# Configuration                                                               #
# ---------------------------------------------------------------------------#

DEFAULT_ENTITY_LABELS: list[str] = ["PERSON", "ORG", "GPE", "PRODUCT"]
_REGEX_FALLBACK_RE = re.compile(r"\b[A-Z][a-z]+(?:\s+[A-Z][a-z]+)*\b")

# ---------------------------------------------------------------------------#
# OpenAI helper                                                               #
# ---------------------------------------------------------------------------#

try:  # noqa: WPS433 – optional dependency
    import openai
except Exception:  # pragma: no cover
    openai = None  # type: ignore[assignment]


def _llm_client() -> Optional[callable]:
    """Return the ChatCompletion.create-like callable, or *None* if unavailable."""
    if openai is None:
        logger.debug("openai SDK not installed.")
        return None

    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        logger.debug("OPENAI_API_KEY env-var missing.")
        return None

    # SDK ≥1.0
    try:
        client = openai.OpenAI(api_key=api_key)  # type: ignore[attr-defined]
        return client.chat.completions.create  # noqa: WPS529
    except AttributeError:
        # SDK <1.0
        openai.api_key = api_key  # type: ignore[attr-defined]
        return openai.ChatCompletion.create  # type: ignore[attr-defined]


@functools.lru_cache(maxsize=256)
def _extract_with_llm_cached(text: str, labels_key: str) -> tuple[str, ...]:
    """Return entities via OpenAI and cache identical requests."""
    chat_create = _llm_client()
    if chat_create is None:
        return ()

    system_prompt = (
        "You are an expert in Named Entity Recognition. "
        f"Extract entities of the following types: {labels_key}. "
        "Respond ONLY with a JSON object whose keys are those labels and "
        "whose values are lists of unique entity strings."
    )

    try:
        resp = chat_create(
            model=os.getenv("OPENAI_NER_MODEL", "gpt-3.5-turbo-0125"),
            temperature=0,
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": text},
            ],
        )
        content = (
            resp["choices"][0]["message"]["content"]  # legacy dict
            if isinstance(resp, dict)
            else resp.choices[0].message.content  # 1.x object
        )
        data: Dict[str, list] = json.loads(content)

        ordered, seen = [], set()
        for label in labels_key.split(", "):  # keep caller's order
            for ent in data.get(label, []):
                if ent not in seen:
                    ordered.append(ent)
                    seen.add(ent)
        return tuple(ordered)
    except Exception as exc:  # pylint: disable=broad-except
        logger.warning("OpenAI extraction failed: %s", exc)
        return ()


def _extract_with_llm(text: str, labels: list[str]) -> list[str] | None:
    ents = _extract_with_llm_cached(text, ", ".join(labels))
    return list(ents) if ents else None


# ---------------------------------------------------------------------------#
# Regex fallback                                                              #
# ---------------------------------------------------------------------------#

def _extract_with_regex(text: str) -> list[str]:
    """Very naive heuristic (capitalised words)."""
    return list(OrderedDict.fromkeys(_REGEX_FALLBACK_RE.findall(text)))


# ---------------------------------------------------------------------------#
# Public API                                                                  #
# ---------------------------------------------------------------------------#

def extract_entities(
    text: str,
    labels: Iterable[str] | None = None,
) -> List[str]:
    """Return a deduplicated list of named entities found in *text*.

    1. Try OpenAI ChatCompletion (high accuracy).
    2. If that's impossible, fall back to the regex heuristic.
    """
    labels_l = list(labels) if labels is not None else DEFAULT_ENTITY_LABELS

    # 1) LLM
    ents = _extract_with_llm(text, labels_l)
    if ents is not None:
        return ents

    # 2) Regex fallback
    return _extract_with_regex(text)
