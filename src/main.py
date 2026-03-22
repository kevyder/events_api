from collections.abc import AsyncGenerator
from contextlib import asynccontextmanager

from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from sqlmodel import SQLModel

# Ensure ORM models are imported so SQLModel.metadata knows about all tables
import src.auth.infrastructure.database.models.user  # noqa: F401
import src.database as database
from src.auth.api.routes import router as auth_router
from src.auth.domain.exceptions import AuthenticationError, AuthorizationError, UserAlreadyExistsError
from src.auth.infrastructure.bootstrap.seed_admin import seed_admin


@asynccontextmanager
async def lifespan(_app: FastAPI) -> AsyncGenerator[None]:
    """Create database tables on startup (dev/test). Use Alembic migrations in production."""
    async with database.engine.begin() as conn:
        await conn.run_sync(SQLModel.metadata.create_all)

    async with database.async_session_factory() as session:
        await seed_admin(session)

    yield


app = FastAPI(title="Events API", version="1.0.0", lifespan=lifespan)

app.include_router(auth_router)


@app.exception_handler(AuthenticationError)
async def authentication_error_handler(_request: Request, exc: AuthenticationError) -> JSONResponse:
    return JSONResponse(status_code=401, content={"detail": str(exc)})


@app.exception_handler(AuthorizationError)
async def authorization_error_handler(_request: Request, exc: AuthorizationError) -> JSONResponse:
    return JSONResponse(status_code=403, content={"detail": str(exc)})


@app.exception_handler(UserAlreadyExistsError)
async def user_already_exists_handler(_request: Request, exc: UserAlreadyExistsError) -> JSONResponse:
    return JSONResponse(status_code=409, content={"detail": str(exc)})
