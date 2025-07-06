from __future__ import annotations
import os
from uuid import uuid4, UUID
import asyncio

from crewai import Agent, Task
from golett_core.crew.golett_crew import GolettCrew
from golett_core.interfaces import MemoryInterface
from golett_core.schemas.memory import ContextBundle
from golett_core.tools.file_tool import FileTool
from golett_core.data_access.memory_dao import MemoryDAO
from golett_core.data_access.vector_dao import VectorDAO
from golett_core.memory.factory import create_memory_core
from golett_core.prompts import UNIVERSAL_SYSTEM_PROMPT

def _format_context_for_crew(bundle: ContextBundle) -> str:
    """Formats a context bundle into a string for crew injection."""
    context_parts = []
    if bundle.retrieved_memories:
        context_parts.append("Relevant Memories:")
        for mem in bundle.retrieved_memories:
            context_parts.append(f"- {mem.content}")
    
    if bundle.recent_history:
        context_parts.append("\nRecent Conversation History:")
        for msg in bundle.recent_history:
            context_parts.append(f"{msg.role.value.capitalize()}: {msg.content}")

    return "\n".join(context_parts)


class Orchestrator:
    """
    Manages the agent crew and orchestrates the chat interaction.
    """
    def __init__(
        self,
        memory_core: MemoryInterface,
        session_id: UUID | None = None,
    ):
        self.session_id = session_id or uuid4()
        self.memory_core = memory_core
        self._setup_crew()

    def _setup_crew(self):
        """Initializes the agents and the crew."""
        # Define agents
        planner = Agent(
            role="Lead Software Planner",
            goal="Plan the execution of a coding task, breaking it down into small, manageable steps.",
            backstory=f"{UNIVERSAL_SYSTEM_PROMPT}\n\nYou are a meticulous planner, excellent at identifying requirements and creating a clear, step-by-step plan for developers to follow. You do not write code.",
            allow_delegation=True,
            verbose=True,
        )
        
        coder = Agent(
            role="Senior Software Engineer",
            goal="Execute a coding plan by writing and modifying files.",
            backstory=f"{UNIVERSAL_SYSTEM_PROMPT}\n\nYou are a skilled engineer who can take a plan and implement it flawlessly using the available file I/O tools. You write clean, efficient code.",
            tools=[FileTool()],
            verbose=True,
        )

        # Assemble the custom crew
        self.crew = GolettCrew(
            agents=[planner, coder],
            tasks=[], # Tasks will be created dynamically
            golett_memory=self.memory_core,
            session_id=self.session_id,
            verbose=True,
        )

    async def run(self, message: str) -> str:
        """
        Main entry point for a user's message.
        """
        # Save the user's message to our memory
        await self.crew.save_user_message(message)
        
        # Get context from memory
        context_bundle = await self.memory_core.search(self.session_id, message)
        crew_context = _format_context_for_crew(context_bundle)

        # Create tasks for the crew
        plan_task = Task(
            description=f"Create a step-by-step plan to address the user's request: '{message}'. The plan should be clear and actionable for a developer.",
            expected_output="A list of numbered steps to be taken.",
            agent=self.crew.agents[0], # Planner
            context=crew_context,
        )
        
        code_task = Task(
            description="Execute the plan created by the planner. Use the file I/O tool to make changes to the filesystem as required by the plan.",
            expected_output="A summary of the file changes made and the final result.",
            agent=self.crew.agents[1], # Coder
            context=[plan_task] # The coding task depends on the planning task
        )
        
        # Update crew with dynamic tasks
        self.crew.tasks = [plan_task, code_task]

        # Kick off the crew and get the result
        result = self.crew.kickoff()
        assistant_response = str(result)

        # Save the final result to our memory
        await self.crew.save_assistant_message(assistant_response)

        return assistant_response


def create_orchestrator(memory_dao: MemoryDAO, vector_dao: VectorDAO) -> Orchestrator:
    """Factory function to easily create an Orchestrator instance."""
    # This check should be at the entry point of your application
    if not os.getenv("OPENAI_API_KEY"):
        raise RuntimeError("OPENAI_API_KEY environment variable not set")
        
    memory_core = create_memory_core(memory_dao, vector_dao)
    return Orchestrator(memory_core)

# Example Usage:
async def main():
    print("Setting up DAOs (placeholders)...")
    # In a real app, these would be properly initialized with connections
    memory_dao = MemoryDAO() 
    vector_dao = VectorDAO()

    print("Creating Orchestrator...")
    orchestrator = create_orchestrator(memory_dao, vector_dao)
    print(f"Chat session started with ID: {orchestrator.session_id}")
    print("---")

    while True:
        user_input = input("You: ")
        if user_input.lower() in ["exit", "quit"]:
            break
        
        print("Agent crew is thinking...")
        response = await orchestrator.run(user_input)
        print(f"Crew: {response}")
        print("---")

if __name__ == "__main__":
    print("This script demonstrates how to use the Orchestrator.")
    print("To run it, you must integrate it into an application with live database connections.")
    # To run the example:
    # try:
    #     asyncio.run(main())
    # except Exception as e:
    #     print(f"Failed to run example: {e}") 