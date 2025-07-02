## Golett Gateway – Coding & Design Guidelines

> **Audience:** All contributors (internal and external)
> **Status:** Draft v0.1 – 2024-06-28

---

### 1. Core principles
1. **Separation of concerns** – Keep I/O, business logic, and orchestration layers distinct.
2. **Interfaces over implementations** – Depend on Python `Protocol`s or abstract base classes, not concrete adapters.
3. **Stateless core** – `golett_core` must be pure functions / classes with no global state; side-effects live in `golett_tools` or `golett_api`.
4. **Evidence lineage** – Every LLM response should carry IDs that trace back to the data it used.
5. **Fail fast, fail loud** – Raise explicit exceptions; do not swallow errors.

---

### 2. Package boundaries & import rules
| Package | May import | Must **not** import |
|---------|-----------|----------------------|
| `golett_core` | stdlib, `typing`, other sub-modules of core | `fastapi`, `sqlalchemy`, external SDKs |
| `golett_tools` | `golett_core`, external SDKs (Qdrant, Cube) | `fastapi.routers` |
| `golett_api` | `fastapi`, `golett_core`, `golett_tools` | direct DB drivers (use adapters) |

Violations are blocked by **ruff**'s `F401` and `I252` import-control rules.

---

### 3. Style & linters
* **Black** – 120-char line length (`pyproject.toml`)
* **Ruff** – error level `E` + `F` + `I`; autofix on commit.
* **Mypy** – strict mode (`--strict`); NO `type: ignore` without a ticket reference.
* **Commit hooks** – Enabled via `pre-commit` config.

Run locally:
```bash
pre-commit run --all-files
```
CI will fail if linting fails.

---

### 4. Project patterns
#### 4.1 Dependency injection
Use `@lru_cache` or Factory functions with FastAPI `Depends`:
```python
from fastapi import Depends
from functools import lru_cache

@lru_cache
def get_qdrant_client() -> QdrantClient:
    return QdrantClient(url=settings.QDRANT_URL, api_key=settings.QDRANT_KEY)

@router.post("/chat")
async def chat(msg: ChatBody, qdrant=Depends(get_qdrant_client)):
    ...
```
No module shall instantiate clients at import time.

#### 4.2 Interface example
```python
class VectorStore(Protocol):
    async def search(self, query: list[float], top_k: int) -> list[VectorMatch]: ...
```
Adapters implement this, tests mock it.

#### 4.3 Result objects
Use **pydantic v2 BaseModel** for cross-layer DTOs; no raw dicts.

**Example: The Pydantic Way vs. The Old Way**

Imagine your API receives a JSON body for a chat message.

**1. The Pydantic Way (✅ DO THIS)**
First, define your data "contract" in `golett_core/schemas.py`:
```python
from uuid import UUID
from typing import Optional, Dict, Any
from pydantic import BaseModel, Field

class ChatMessage(BaseModel):
    session_id: UUID
    content: str = Field(..., min_length=1)
    metadata: Optional[Dict[str, Any]] = None
```
Then, use it in your API. FastAPI handles all validation automatically.
```python
# In golett_api/routers/chat.py
from golett_core.schemas import ChatMessage

@router.post("/chat")
async def handle_chat(message: ChatMessage):
    # If code reaches here, `message` is a guaranteed-clean object.
    # No validation needed. FastAPI already did it.
    # If data was bad, a 422 error was already returned.
    return await process_user_message(message)
```
This is clean, robust, and self-documenting.

**2. The Old Way (❌ DO NOT DO THIS)**
Without Pydantic, you end up with messy, manual validation code.
```python
@router.post("/chat")
async def handle_chat_old_way(data: dict):
    if not data.get("session_id") or not data.get("content"):
        raise HTTPException(status_code=400, detail="Missing fields")
    if not isinstance(data["content"], str) or len(data["content"]) == 0:
        raise HTTPException(status_code=400, detail="Invalid content")
    # ...and so on for every field and type. This is brittle.
    return await process_user_message_old_way(data)
```
This is verbose, error-prone, and hard to maintain.

#### 4.4 Schema migrations (Flyway)
We manage **all** database changes through Flyway SQL migrations—never via runtime DDL.

* Migration files live in `infra/migrations`
* Naming convention: `V<YYYYMMDD>__<short_desc>.sql` (example: `V20240628__create_sessions.sql`)
* Use **pure SQL**; Flyway will wrap them in a transaction.
* One DDL concern per file; avoid mixing schema + data fixes.
* To create a new migration:
  ```bash
  ./scripts/new-migration.sh "add_index_on_messages_created_at"
  ```
  (The helper script stamps the date prefix.)
* Local workflow:
  ```bash
  docker compose up -d db
  flyway migrate -url=$DB_URL -user=$DB_USER -password=$DB_PASS -locations=filesystem:infra/migrations
  ```
* CI pipeline runs the same `flyway migrate`, so keep scripts idempotent.

> **Rule**: If your PR changes the ORM models or raw SQL queries **and** requires a new column/index/table, add a Flyway script in the same commit.

---

### 5. Testing strategy
We follow a three-tiered testing pyramid to ensure correctness without sacrificing speed.

| Test Type | Scope | Tooling | Speed |
|---|---|---|---|
| **Unit Tests** | Single function/class in isolation. **No network, no DB.** | `pytest`, `unittest.mock`, in-memory fakes | Blazing fast (<1s per module) |
| **Integration Tests** | Interaction between components (e.g., API ↔ DB adapter). | `pytest-docker`, `httpx` | Slow (~seconds per test) |
| **E2E Tests** | Full user flow through a deployed environment. | (e.g., Playwright, k6) | Slowest (~minutes per run) |

**Key Rules:**
* **Unit tests MUST be pure.** They test logic, not I/O. Use mock objects or in-memory fakes (e.g., a `dict` that pretends to be Redis) injected via FastAPI's `Depends` overrides.
* **Integration tests use `pytest-docker`** to spin up real services (Postgres, Qdrant). Mark these tests with `@pytest.mark.integration` to run them separately from fast unit tests.
  ```bash
  # Run only fast unit tests
  pytest -m "not integration"

  # Run only slow integration tests (typically in CI)
  pytest -m "integration"
  ```
* **Coverage targets:** Aim for >90% unit test coverage on core logic (`golett_core`) and targeted integration tests for all external-facing contracts (API endpoints, DB schemas).

---

### 6. Logging & metrics
* Use `golett_utils.logger.get_logger`.
* Log level `INFO` in prod, `DEBUG` only under `GOLETT_LOG_LEVEL=DEBUG`.
* Include `session_id`, `trace_id` in every log entry (`structlog` planned).
* Expose Prometheus metrics under `/metrics`; add a counter for every external call.

---

### 7. Pull-request checklist
- [ ] PR builds & tests green
- [ ] Added/updated docstrings & type hints
- [ ] Updated CHANGELOG
- [ ] No TODOs without linked issue
- [ ] Required Flyway migration added & tested
- [ ] If adding dependency → justified in PR description

---

### 8. Future evolution
* Enforce architectural import rules with `flake8-import-order` plugin.
* Move to **typed-dict** and **dataclass-transform** once on Python 3.12.

---

*Happy coding!* 