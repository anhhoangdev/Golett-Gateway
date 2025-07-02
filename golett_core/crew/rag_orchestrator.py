from __future__ import annotations

"""Orchestrator tailored for retrieval-augmented answering (RAG) crews.

Unlike the coding-focused `golett_core.crew.orchestrator.Orchestrator`,
this variant contains *researcher* and *writer* agents that collaborate to
produce factually-grounded answers leveraging the shared
`KnowledgeHandler` data-store.
"""

from uuid import uuid4, UUID
from typing import List

from crewai import Agent, Task

from golett_core.interfaces import MemoryInterface
from golett_core.crew.golett_crew import GolettCrew
from golett_core.schemas.memory import ChatMessage, ChatRole
from golett_core.interfaces import KnowledgeInterface

__all__ = [
    "RAGOrchestrator",
]


class RAGOrchestrator:
    """Manages a two-agent RAG workflow (research → write)."""

    def __init__(
        self,
        memory_core: MemoryInterface,
        knowledge_handler: KnowledgeInterface,
        session_id: UUID | None = None,
    ) -> None:  # noqa: D401
        self.session_id = session_id or uuid4()
        self.memory_core = memory_core
        self.knowledge = knowledge_handler
        self._setup_crew()

    # ------------------------------------------------------------------
    # Crew definition
    # ------------------------------------------------------------------

    def _setup_crew(self) -> None:  # noqa: D401
        researcher = Agent(
            role="Researcher",
            goal="Search the knowledge base and extract the most relevant facts to answer the user's query.",
            backstory="You excel at focused information retrieval and note-taking.",
            allow_delegation=False,
            verbose=True,
        )

        writer = Agent(
            role="Technical Writer",
            goal="Craft a clear, concise and accurate answer based on the provided research notes.",
            backstory="You transform raw research notes into user-friendly explanations, citing facts when appropriate.",
            verbose=True,
        )

        self.crew = GolettCrew(
            agents=[researcher, writer],
            tasks=[],  # tasks are generated per message
            golett_memory=self.memory_core,
            session_id=self.session_id,
            verbose=True,
        )

    # ------------------------------------------------------------------

    async def run(self, message: str) -> str:  # noqa: D401
        """Process a user *message* through the RAG workflow."""
        # ----- Persist user message in memory --------------------------------
        await self.crew.save_user_message(message)

        # Retrieve memory context (short-term & long-term) ---------------------------------
        mem_bundle = await self.memory_core.search(self.session_id, message, include_recent=True)
        mem_snippets = [itm.content for itm in mem_bundle.retrieved_memories][:5]

        # Retrieve knowledge snippets ------------------------------------------------------
        kb_snippets: List[str] = []
        if self.knowledge is not None:
            kb_snippets = await self.knowledge.get_retrieval_context(
                query=message,
                chat_history=[],
                top_k=5,
            )

        snippets = mem_snippets + kb_snippets
        joined_snippets = "\n".join(snippets) if snippets else "(no snippets)"

        # ----- Build tasks ----------------------------------------------------
        research_task = Task(
            description=(
                "Search the knowledge snippets provided below and produce a set\n"
                "of bullet-point facts that directly answer the user's query.\n\n"
                f"User Query: {message}\n\nKnowledge Snippets:\n{joined_snippets}"
            ),
            expected_output="Bullet-point notes with relevant facts (no prose).",
            agent=self.crew.agents[0],  # Researcher
        )
        write_task = Task(
            description="Compose the final answer for the user in clear prose, citing facts from the research notes when useful.",
            expected_output="The assistant's final response.",
            agent=self.crew.agents[1],  # Writer
            context=[research_task],
        )

        self.crew.tasks = [research_task, write_task]

        # ----- Kick off -------------------------------------------------------
        result = self.crew.kickoff()
        assistant_response = str(result)

        # ----- Persist assistant message -------------------------------------
        await self.crew.save_assistant_message(assistant_response)
        return assistant_response 