"""Light-weight content tagging utilities.

A Tagger assigns high-level metadata (message_type, topic, importance) to
incoming ChatMessage objects so downstream memory workers can make
content-aware decisions (e.g. which messages should be summarised).

This first version relies on an LLM call.  If latency/cost become a
concern the prompt can be distilled into a smaller model or a simple
keyword/regex heuristic.
"""
from __future__ import annotations

import os
from typing import Dict, Literal, List

import openai

from golett_core.schemas.memory import ChatMessage
from golett_core.interfaces import TaggerInterface
from golett_core.memory.retrieval.entity_extraction import extract_entities

MessageType = Literal["FACT", "PREFERENCE", "PLAN", "CHITCHAT"]


class LLMTagger:
    """Assigns (type, importance, topic) using a single chat completion call."""

    def __init__(self, model: str = "gpt-3.5-turbo-0125") -> None:
        self.model = model
        api_key = os.getenv("OPENAI_API_KEY")
        if not api_key:
            raise RuntimeError("OPENAI_API_KEY environment variable not set")
        openai.api_key = api_key

    async def tag(self, msg: ChatMessage) -> Dict[str, str | float]:  # noqa: D401
        """Return a dict with keys: type, importance, topic.

        importance is a float 0-1.  topic is a short noun phrase <= 4 words.
        """
        system = (
            "You are a classifier that labels chat turns for an AI memory system.\n"
            "Given the user or assistant message, respond in JSON with exactly these keys: \n"
            "type (one of FACT, PREFERENCE, PLAN, CHITCHAT),\n"
            "importance (float 0-1 where 1 is vital knowledge),\n"
            "topic (2-4 word noun phrase summarising the subject).\n"
            "Think step-by-step internally but output *only* the JSON object."
        )
        user = msg.content
        resp = await openai.ChatCompletion.acreate(  # type: ignore[attr-defined]
            model=self.model,
            messages=[{"role": "system", "content": system}, {"role": "user", "content": user}],
            temperature=0.0,
        )
        import json

        try:
            data = json.loads(resp.choices[0].message.content)
        except Exception:
            # Fallback – treat as chit-chat unimportant.
            data = {"type": "CHITCHAT", "importance": 0.0, "topic": "general"}
        # Ensure correct types.
        data["importance"] = float(data.get("importance", 0.0))
        return data


class RuleTagger:
    """Ultra-lightweight heuristic fallback if LLM access is unavailable."""

    async def tag(self, msg: ChatMessage) -> Dict[str, str | float]:  # noqa: D401
        text = msg.content.lower()
        if any(k in text for k in ["i like", "i prefer", "my favorite"]):
            return {"type": "PREFERENCE", "importance": 0.4, "topic": "user preference"}
        if "plan" in text or "let's" in text:
            return {"type": "PLAN", "importance": 0.3, "topic": "plan"}
        return {"type": "CHITCHAT", "importance": 0.1, "topic": "general"}


class AutoTagger:
    """Smart wrapper: use LLM if credentials present, otherwise rule-based."""

    def __init__(self, model: str | None = None) -> None:
        self._llm: TaggerInterface | None = None
        if os.getenv("OPENAI_API_KEY"):
            self._llm = LLMTagger(model=model or "gpt-3.5-turbo-0125")
        self._rule = RuleTagger()

    async def tag(self, msg: ChatMessage):
        """Return tagging metadata enriched with automatically extracted entities.

        The base tagger (LLM or rule) assigns *type*, *importance*, and *topic*.
        We post-process the result to also include:

        - ``entities``: list\[dict\] where each dict has **id** and **type** keys.
          Entity IDs are simple string identifiers for now (e.g. "person:JaneDoe").
        - ``relations``: list\[dict\] placeholder for future relation extraction.

        Down-stream workers such as ``GraphWorker`` can use these fields to
        populate the knowledge graph.
        """

        # ---------------- Select underlying tagger ----------------
        base_tags: Dict[str, str | float]
        if self._llm:
            try:
                base_tags = await self._llm.tag(msg)
            except Exception:
                # fall through to rule tagger on any failure
                base_tags = await self._rule.tag(msg)
        else:
            base_tags = await self._rule.tag(msg)

        # ---------------- Entity extraction ----------------
        entities: List[Dict[str, str]] = [
            {"id": ent, "type": "Entity"} for ent in extract_entities(msg.content)
        ]

        # Currently no automated relation extraction implemented – keep empty list
        relations: List[Dict[str, str]] = []

        base_tags["entities"] = entities
        base_tags["relations"] = relations

        return base_tags
