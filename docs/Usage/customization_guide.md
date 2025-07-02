# Customization Guide

This guide details how to extend and customize the Golett Core framework. Thanks to its modular, protocol-driven design, you can easily swap out components, register new functionality, and change behavior without forking the core codebase.

## 1. Swapping Memory or Knowledge Back-ends

The memory and knowledge systems are abstracted behind `MemoryInterface` and `KnowledgeInterface` protocols. You can provide any object that conforms to the required interface.

### Example: Using a Custom Memory Back-end

First, implement the `MemoryInterface` protocol:

```python
# my_project/custom_memory.py
from golett_core.interfaces import MemoryInterface
from golett_core.schemas import ChatMessage, ContextBundle

class MyAwesomeMemory(MemoryInterface):
    async def save_message(self, msg: ChatMessage) -> None:
        print(f"Saving '{msg.content}' to my awesome storage!")
        # ... your implementation ...

    async def search(self, session_id, query, **kwargs) -> ContextBundle:
        print(f"Searching for '{query}' in my awesome storage!")
        # ... your implementation ...
        return ContextBundle(...)
```

Then, inject it using the `GolettBuilder`:

```python
# my_project/main.py
from golett_core.builder import GolettBuilder
from .custom_memory import MyAwesomeMemory

app = (
    GolettBuilder()
    .with_memory(MyAwesomeMemory())
    .build()
)

await app.chat("session-123", "Hello, custom world!")
```

The same principle applies to `with_knowledge(MyKnowledge())`.

## 2. Registering New Crews

Crews are dynamically selected based on registered `CrewSpec` objects. You can add your own crews to handle new types of tasks.

### Example: Registering a "Code Review" Crew

First, define a `CrewSpec`:

```python
# my_project/review_crew.py
from golett_core.crew.spec import CrewSpec, register_spec

def is_code_review_request(message: str) -> bool:
    return "review my code" in message.lower()

# Create the spec
code_review_spec = CrewSpec(
    name="code_review_crew",
    description="A crew that specializes in reviewing code for quality.",
    match_fn=is_code_review_request,
    requires_knowledge=False,  # Or True if it needs to access knowledge
)

# Register it
register_spec(code_review_spec)
```

Now, simply import this module in your application's entry point. The builder will automatically pick it up.

```python
# my_project/main.py
from golett_core.builder import GolettBuilder
from . import review_crew  # This import triggers the registration

app = GolettBuilder().build()

# This message will now be routed to your custom crew
await app.chat("session-456", "Can you review my code?")
```

## 3. Creating Custom Tools

Agents use tools that conform to the `ToolInterface` protocol (which is compatible with `crewai.tools.BaseTool`).

### Example: A Simple Calculator Tool

```python
# my_project/tools.py
from typing import Type
from pydantic import BaseModel, Field
from golett_core.interfaces import ToolInterface

class CalculatorSchema(BaseModel):
    expression: str = Field(description="The mathematical expression to evaluate.")

class CalculatorTool(ToolInterface):
    name: str = "Calculator"
    description: str = "Evaluates a mathematical expression."
    args_schema: Type[BaseModel] = CalculatorSchema

    def run(self, expression: str) -> str:
        try:
            return str(eval(expression))
        except Exception as e:
            return f"Error: {e}"
```

While the `GolettBuilder` has a `with_tools` method, tool assignment is typically done at the `Agent` level within a custom crew's orchestrator.

## 4. Relaxing Schema Strictness

By default, all Pydantic models operate in `"strict"` mode, forbidding extra fields. You can switch the entire application to `"lax"` mode, which allows extra fields, by setting an environment variable.

Create a `.env` file in your project root:

```dotenv
# .env
PYDANTIC_MODE="lax"
```

The `GolettBuilder` will automatically load this setting, and all models will now accept arbitrary extra fields, which can be useful for development or for attaching custom data to objects. 