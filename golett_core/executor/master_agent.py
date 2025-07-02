from __future__ import annotations

"""Lightweight *Master Agent* responsible for selecting the right crew.

This implementation keeps the routing logic extremely simple and
rule-based so that we do not need to call a full-blown LLM.  Developers
can later swap the :py:meth:`_select_spec` strategy with a more advanced
classifier without touching the public interface.
"""

from typing import List

from golett_core.crew.spec import CrewSpec, default_specs
from golett_core.schemas.memory import ChatMessage
from golett_core.interfaces import CrewFactoryInterface

__all__ = [
    "MasterAgent",
]


class MasterAgent:
    """Routes an incoming user prompt to the most appropriate crew."""

    def __init__(
        self,
        crew_factory: CrewFactoryInterface,
        specs: List[CrewSpec] | None = None,
    ) -> None:  # noqa: D401
        self._factory = crew_factory
        # Specs priority is their list order – first match wins
        self._specs: List[CrewSpec] = specs or default_specs()

    # ------------------------------------------------------------------

    async def run(self, user_message: str, history: List[ChatMessage]) -> str:  # noqa: D401
        """Pick a crew, execute it, and return the assistant reply."""
        spec = await self._pick_spec(user_message)
        # For now we simply use the *user_message* as the prompt; the crew
        # itself already has access to chat history via memory search.
        return await self._factory.create_and_run(spec, user_message, history)

    # ------------------------------------------------------------------

    async def _pick_spec(self, message: str) -> CrewSpec:  # noqa: D401
        """Return the first spec whose ``match_fn`` yields ``True``."""
        # Let each registered CrewSpec decide if it matches. More
        # sophisticated logic (LLM-based, metadata-aware…) can be plugged
        # in later without changing the public interface.
        for spec in self._specs:
            if spec.match_fn(message):
                return spec

        # As a safety net, fallback to the *last* spec (should be a generic
        # conversation crew).
        return self._specs[-1] 