# Events API

[![CI](https://github.com/kevyder/fastapi_template/actions/workflows/ci.yml/badge.svg?branch=master)](https://github.com/kevyder/fastapi_template/actions/workflows/ci.yml)
[![Coverage Status](https://coveralls.io/repos/github/kevyder/events_api/badge.svg?branch=master)](https://coveralls.io/github/kevyder/events_api?branch=master)

A RESTful API for managing events, sessions, and participation built with FastAPI and Python.

## Summary

Events API is a backend service that allows administrators to create and manage events with sessions, while regular users can browse events and join them as participants. The project features JWT-based authentication with role-based access control (admin and user roles), paginated listings with search, session scheduling with overlap prevention, and automatic event status synchronization based on capacity. It is built following hexagonal architecture (ports & adapters) on top of PostgreSQL with async SQLAlchemy, and ships fully containerized with Docker Compose.

## Requirements

- Python 3.13+
- Docker & Docker Compose
- [uv](https://docs.astral.sh/uv/) for local development

## Project Structure

```
src/
  main.py                                   # FastAPI app, lifespan, exception handlers
  config.py                                 # Settings (env vars)
  database.py                               # Async engine & session factory
  auth/                                     # Authentication bounded context
    api/
      routes.py                             # Auth HTTP endpoints
      schemas.py                            # Pydantic request/response models
      dependencies.py                       # FastAPI Depends() wiring
    domain/
      models.py                             # User entity, Role enum
      contracts.py                          # Abstract interfaces (password hasher, token service)
      exceptions.py                         # Auth domain exceptions
      repositories.py                       # UserRepository port (ABC)
    infrastructure/
      bootstrap/
        seed_admin.py                       # Seeds default admin on startup
      database/
        models/
          user.py                           # UserModel (SQLAlchemy ORM)
        repositories/
          user_repository.py                # SQLAlchemy UserRepository adapter
      security/
        bcrypt_password_hasher.py           # Bcrypt adapter
        jwt_token_service.py                # JWT adapter
    use_cases/
      register_user.py                      # User registration
      login_user.py                         # User login (returns JWT)
      get_current_user.py                   # Token validation
  event/                                    # Event management bounded context
    api/
      routes.py                             # Event HTTP endpoints
      schemas.py                            # Pydantic request/response models
      dependencies.py                       # FastAPI Depends() wiring
    domain/
      models.py                             # Event, Session, Status entities
      exceptions.py                         # Event domain exceptions
      repositories.py                       # EventRepository port (ABC)
    infrastructure/
      database/
        models/
          event.py                          # EventModel (ORM)
          session.py                        # SessionModel (ORM)
          participant.py                    # EventParticipantModel (ORM)
        repositories/
          event_repository.py               # SQLAlchemy EventRepository adapter
    use_cases/
      list_events.py                        # Paginated event listing
      search_events.py                      # Search events by name
      list_my_events.py                     # List user's joined events
      get_event.py                          # Get event with sessions
      create_event.py                       # Create event
      update_event.py                       # Partial update with status sync
      delete_event.py                       # Delete event (cascades)
      create_session.py                     # Create session (overlap check)
      update_session.py                     # Update session (overlap check)
      delete_session.py                     # Delete session
      participate_in_event.py               # Join event (status sync)
      leave_event.py                        # Leave event (status sync)
tests/
  conftest.py                               # Shared fixtures, test DB setup
  auth/
    api/test_routes.py                      # Auth integration tests
    domain/test_models.py                   # User model unit tests
    infrastructure/
      bootstrap/test_seed_admin.py          # Seed admin unit tests
    use_cases/
      test_get_current_user.py
      test_login_user.py
      test_register_user.py
  event/
    api/test_routes.py                      # Event integration tests
    domain/test_models.py                   # Event/Session model unit tests
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

## Running the Project

### Development

Build and start the application with PostgreSQL:

```sh
docker compose up --build
```

The API will be available at `http://localhost:8080`. A default admin user is seeded on startup using the credentials defined in the compose file.

### Tests

Run the full test suite with coverage inside Docker:

```sh
docker compose -f docker-compose.test.yml up --build --abort-on-container-exit
```

This spins up an isolated PostgreSQL instance, runs all tests with `pytest`, and reports code coverage. The `--abort-on-container-exit` flag ensures the command exits with the test process exit code, making it suitable for CI pipelines.

## API Documentation

Interactive Swagger UI documentation is available at:

```
http://localhost:8080/docs
```

All endpoints, request/response schemas, and authentication requirements are documented there automatically by FastAPI.

## API Endpoints

### Auth

| Method | Path | Description | Access |
|--------|------|-------------|--------|
| `POST` | `/auth/sign-up` | Register a new user | Public |
| `POST` | `/auth/sign-up-admin` | Register a new admin | Admin |
| `POST` | `/auth/login` | Authenticate and get JWT | Public |
| `GET` | `/auth/me` | Get current user profile | Authenticated |

### Events

| Method | Path | Description | Access |
|--------|------|-------------|--------|
| `GET` | `/events` | List events (paginated) | Public |
| `GET` | `/events/search?name=` | Search events by name | Public |
| `GET` | `/events/me/participations` | List events the user has joined | Authenticated |
| `GET` | `/events/{event_id}` | Get event details with sessions | Public |
| `POST` | `/events` | Create an event | Admin |
| `PATCH` | `/events/{event_id}` | Partially update an event | Admin |
| `DELETE` | `/events/{event_id}` | Delete an event | Admin |

### Sessions

| Method | Path | Description | Access |
|--------|------|-------------|--------|
| `POST` | `/events/{event_id}/sessions` | Create a session | Admin |
| `PATCH` | `/events/{event_id}/sessions/{session_id}` | Update a session | Admin |
| `DELETE` | `/events/{event_id}/sessions/{session_id}` | Delete a session | Admin |

### Participation

| Method | Path | Description | Access |
|--------|------|-------------|--------|
| `POST` | `/events/{event_id}/participate` | Join an event | Authenticated |
| `DELETE` | `/events/{event_id}/participate` | Leave an event | Authenticated |

## Architecture

This project follows **hexagonal architecture** (also known as ports & adapters), which organizes code into concentric layers with clear dependency rules:

```
API (inbound adapter)
  -> Use Cases (application logic)
    -> Domain (entities, rules, port interfaces)
      <- Infrastructure (outbound adapters: DB, external services)
```

**Domain** contains pure business entities (`Event`, `Session`, `User`), validation rules, and abstract port interfaces (`EventRepository`, `UserRepository`). It has zero dependencies on frameworks or libraries.

**Use Cases** orchestrate application logic by combining domain operations. They depend only on port interfaces, never on concrete implementations.

**Infrastructure** provides concrete adapters that implement the domain ports: SQLAlchemy repositories for persistence, bcrypt for password hashing, JWT for token generation.

**API** is the inbound HTTP adapter. FastAPI routes receive requests, delegate to use cases, and map domain exceptions to HTTP responses. Dependency injection wires adapters to ports via `Depends()`.

This separation ensures that business logic is testable in isolation (unit tests mock ports), framework changes stay contained in the outer layers, and each bounded context (`auth`, `event`) is self-contained.

## Code Quality

### Pre-commit Hooks

The project uses [pre-commit](https://pre-commit.com/) to enforce quality checks before every commit:

- **ruff** -- linting with auto-fix and code formatting
- **trailing-whitespace** and **end-of-file-fixer** -- file hygiene
- **check-yaml** and **check-added-large-files** -- safety checks
- **conventional-pre-commit** -- enforces [Conventional Commits](https://www.conventionalcommits.org/) message format

Setup:

```sh
uv sync --group dev
pre-commit install
```

### Ruff

[Ruff](https://docs.astral.sh/ruff/) handles both linting and formatting in a single tool. Enabled rule sets:

| Rule | Scope |
|------|-------|
| `E` | pycodestyle errors |
| `F` | Pyflakes (unused imports, undefined names) |
| `UP` | pyupgrade (modern Python syntax) |
| `B` | flake8-bugbear (common bugs) |
| `SIM` | flake8-simplify (code simplification) |
| `I` | isort (import sorting) |

Configuration lives in `pyproject.toml` with a 120-character line length and double-quote style.

## Why uv?

This project uses [uv](https://docs.astral.sh/uv/) instead of Poetry for dependency management. uv is built in Rust and is orders of magnitude faster for dependency resolution and installation -- a full `uv sync` completes in seconds where Poetry can take minutes. It works natively with the standard `pyproject.toml` format without requiring a Poetry-specific `[tool.poetry]` section, keeping the project compatible with PEP 621. It also handles virtual environment creation, lockfile generation, and dependency groups in a single tool with a simpler mental model than Poetry's split between `pyproject.toml` and `poetry.lock` workflows.
