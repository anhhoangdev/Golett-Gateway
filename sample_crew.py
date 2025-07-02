from __future__ import annotations

"""sample_crew.py – Quick interactive demo for `golett_core`

Run this file after setting the ``OPENAI_API_KEY`` environment variable to see
Golett's agent crew in action directly from the terminal::

    $ export OPENAI_API_KEY=sk-...
    $ python sample_crew.py

The script uses the GolettBuilder, which defaults to in-memory stores, so it
requires *no* Postgres or Qdrant instances to get started.
"""

import asyncio
import os
from typing import NoReturn
from uuid import uuid4
from dotenv import load_dotenv
from rich.console import Console
from rich.panel import Panel

from golett_core.builder import GolettBuilder

load_dotenv()

# -------------------------------------------------------------
# Configuration helper
# -------------------------------------------------------------

PERSISTENT = os.getenv("GOLETT_PERSISTENT", "false").lower() in {"1", "true", "yes"}

async def _run_interactive() -> None:  # noqa: D401 – simple CLI helper
    """Spawn an interactive REPL with the sample crew."""

    # 1. Build the Golett app – choose storage backend based on env var
    builder = GolettBuilder()
    if PERSISTENT:
        print("🗄   Using Postgres + Qdrant + PG-Graph persistent stores…")
        builder.with_persistent_stores()
    else:
        print("🧪  Using in-memory stores – no external services required…")
        builder.with_in_memory_stores()

    app = builder.build()
    print("Build complete.")

    # 2. Start a new session
    session_id = uuid4()

    print("\n🗿  Golett Sample Crew")
    print(f"Session ID: {session_id}")
    print("The default crew can answer questions (e.g., 'What is crewAI?')")
    print("and perform coding tasks (e.g., 'create a file named hello.txt').")
    print("Type 'exit' or 'quit' to leave the demo.\n")

    # ------------------------------------------------------------------
    # 3. Simple REPL loop
    # ------------------------------------------------------------------

    while True:
        try:
            user_input = input("You > ")
        except (EOFError, KeyboardInterrupt):
            print("\nGoodbye!")
            break

        if user_input.strip().lower() in {"exit", "quit"}:
            print("Exiting…")
            break

        if not user_input.strip():
            continue

        print("\nCrew is thinking…\n")
        assistant_reply = await app.chat(session_id, user_input)
        print(f"Crew > {assistant_reply}\n")


def main() -> NoReturn:  # noqa: D401 – entry-point wrapper
    """Validate environment & dispatch the async entry-point."""
    if not os.getenv("OPENAI_API_KEY"):
        raise RuntimeError("Please set the OPENAI_API_KEY environment variable before running the demo.")

    try:
        asyncio.run(_run_interactive())
    except KeyboardInterrupt:
        print("\nInterrupted. Bye!")


if __name__ == "__main__":
    main() 