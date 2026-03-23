# AGENTS.md — events_api

Guidelines for AI coding agents working in this repository.

## Project Overview

Events API — a FastAPI application for managing events, sessions, and user participation.
Two bounded contexts: **auth** (registration, login, JWT) and **event** (CRUD, sessions, participation).
Uses **hexagonal architecture** (ports & adapters) with async SQLAlchemy on PostgreSQL.
Runtime: Python 3.13+ | Framework: FastAPI 0.135.1 | Package manager: uv

## Build & Run Commands

```bash
# Install dependencies
uv sync --group test          # runtime + test deps
uv sync --group dev           # runtime + dev deps (ruff, pre-commit)
uv sync --no-dev              # runtime only (production)

# Run the application
uvicorn src.main:app --reload --host 0.0.0.0 --port 8080

# Run ALL tests
pytest --verbosity=2

# Run a SINGLE test file
pytest tests/test_main.py --verbosity=2

# Run a SINGLE test function
pytest tests/test_main.py::test_read_root --verbosity=2

# Run tests by keyword expression
pytest -k "test_read_root" --verbosity=2

# Run tests with coverage
pytest --cov=src --verbosity=2

# Run tests in Docker
docker compose -f docker-compose.test.yml up --build

# Lint and format
ruff check --fix .             # lint with auto-fix
ruff format .                  # format code
pre-commit run --all-files     # run all pre-commit hooks

# Check lint without fixing
ruff check .
ruff format --check .
```

## Hexagonal Architecture

This project follows hexagonal architecture (ports & adapters). Organize code as:

```
src/
  main.py                      # FastAPI app creation, lifespan, exception handlers
  config.py                    # Settings (env vars)
  database.py                  # Async engine & session factory
  auth/                        # bounded context: authentication
    api/
      routes.py                # Auth HTTP endpoints (inbound adapter)
      schemas.py               # Pydantic request/response models
      dependencies.py          # FastAPI Depends() wiring
    domain/
      models.py                # User entity, Role enum
      contracts.py             # Abstract interfaces (password hasher, token service)
      exceptions.py            # Auth domain exceptions
      repositories.py          # UserRepository port (ABC)
    infrastructure/
      bootstrap/
        seed_admin.py          # Seeds default admin on startup
      database/
        models/
          user.py              # UserModel (SQLAlchemy ORM)
        repositories/
          user_repository.py   # SQLAlchemy UserRepository adapter
      security/
        bcrypt_password_hasher.py
        jwt_token_service.py
    use_cases/
      register_user.py
      login_user.py
      get_current_user.py
  event/                       # bounded context: event management
    api/
      routes.py                # Event HTTP endpoints (inbound adapter)
      schemas.py               # Pydantic request/response models
      dependencies.py          # FastAPI Depends() wiring
    domain/
      models.py                # Event, Session, Status entities
      exceptions.py            # Event domain exceptions
      repositories.py          # EventRepository port (ABC)
    infrastructure/
      database/
        models/
          event.py             # EventModel (ORM)
          session.py           # SessionModel (ORM)
          participant.py       # EventParticipantModel (ORM)
        repositories/
          event_repository.py  # SQLAlchemy EventRepository adapter
    use_cases/
      list_events.py
      search_events.py
      list_my_events.py
      get_event.py
      create_event.py
      update_event.py
      delete_event.py
      create_session.py
      update_session.py
      delete_session.py
      participate_in_event.py
      leave_event.py
tests/
  conftest.py                  # shared fixtures, test DB setup
  auth/
    api/test_routes.py
    domain/test_models.py
    infrastructure/bootstrap/test_seed_admin.py
    use_cases/
      test_get_current_user.py
      test_login_user.py
      test_register_user.py
  event/
    api/test_routes.py
    domain/test_models.py
    use_cases/
      test_list_events.py
      test_search_events.py
      test_list_my_events.py
      test_get_event.py
      test_create_event.py
      test_update_event.py
      test_delete_event.py
      test_create_session.py
      test_update_session.py
      test_participate_in_event.py
      test_leave_event.py
```

**Key rules:**
- Domain layer has ZERO framework dependencies (no FastAPI, no SQLAlchemy, no Pydantic).
- Domain defines ports (abstract interfaces). Infrastructure provides adapters (implementations).
- Application services depend on ports, never on concrete adapters.
- Dependency injection: wire adapters to ports via FastAPI `Depends()` in the API layer.
- Flow: API route -> application service -> domain logic -> port -> adapter.

## Code Style

### Formatting (enforced by ruff)
- **Line length:** 120 characters max
- **Quotes:** double quotes (`"`)
- **Indentation:** spaces (4 spaces)
- **Docstrings:** Google convention
- **Files:** must end with a newline, no trailing whitespace

### Imports
Ordered by ruff's isort rules (`I`) with a blank line between groups:
1. Standard library
2. Third-party packages
3. Local/project imports (`from src. ...`)

```python
import os
from typing import Protocol

from fastapi import APIRouter, Depends

from src.events.domain.ports import EventRepository
```

### Naming Conventions
- **Functions / methods:** `snake_case`
- **Variables:** `snake_case`
- **Classes:** `PascalCase`
- **Modules / files:** `snake_case`
- **Constants:** `UPPER_SNAKE_CASE`
- **Private:** prefix with single underscore (`_internal_method`)
- **Pydantic models / schemas:** `PascalCase` with descriptive suffix (`EventCreateRequest`, `EventResponse`)
- **Domain ports (ABCs):** `PascalCase` noun describing the capability (`EventRepository`, `NotificationService`)

### Type Annotations
- Use type annotations on all function signatures (parameters and return types).
- Use `typing.Protocol` or `abc.ABC` for domain port interfaces.
- Use Pydantic `BaseModel` for API schemas and DTOs.
- Domain models should be plain Python classes or dataclasses — not Pydantic models.

### Async
- FastAPI route handlers: use `async def`.
- Application services: use `async def` when they call async adapters.
- Domain logic: prefer synchronous (pure functions/methods).

### Error Handling
- Define domain exceptions in `domain/exceptions.py` (inherit from a base `DomainException`).
- Application services raise domain exceptions.
- API layer catches domain exceptions and maps them to HTTP responses using FastAPI exception handlers.
- Never let raw infrastructure exceptions (DB errors, HTTP errors) leak into the domain or API layer.
- Use FastAPI's `HTTPException` only in the API layer.

```python
# domain/exceptions.py
class DomainException(Exception):
    pass

class EventNotFoundError(DomainException):
    def __init__(self, event_id: str):
        super().__init__(f"Event {event_id} not found")
```

### Testing
- Framework: **pytest** (synchronous tests with `TestClient`).
- Test files mirror source structure: `src/events/domain/models.py` -> `tests/events/domain/test_models.py`.
- Test function names: `test_<what_is_being_tested>` — descriptive, snake_case.
- Use `conftest.py` for shared fixtures (test clients, mock adapters, factories).
- Unit test domain logic and application services by mocking ports.
- Integration test API routes using `fastapi.testclient.TestClient`.
- No test classes — use plain functions.

### Commit Messages
Enforced by pre-commit: **Conventional Commits** format.
```
feat: add event creation endpoint
fix: handle missing event_id in update
refactor: extract event validation to domain service
test: add unit tests for event model
chore: update dependencies
docs: add API usage examples to README
```

## Ruff Lint Rules

Enabled rule sets in `pyproject.toml`:
| Rule | Scope |
|------|-------|
| `E`  | pycodestyle |
| `F`  | Pyflakes (unused imports, undefined names) |
| `UP` | pyupgrade (modern Python syntax) |
| `B`  | flake8-bugbear (common bugs) |
| `SIM`| flake8-simplify (code simplification) |
| `I`  | isort (import sorting) |

Ignored: `E203`, `E305`

## CI/CD

GitHub Actions on push/PR to `master`:
- **test** job: pytest on Python 3.13.9 and 3.14.0
- **lint** job: pre-commit hooks (ruff check, ruff format, trailing whitespace, YAML validation)

## Docker

```bash
docker compose up --build                                                   # dev with hot reload on port 8080
docker compose -f docker-compose.test.yml up --build --abort-on-container-exit  # run tests with coverage
```
