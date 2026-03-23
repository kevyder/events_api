from collections.abc import AsyncGenerator
from contextlib import asynccontextmanager

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from fastapi_pagination import add_pagination

import src.database as database
from src.auth.api.routes import router as auth_router
from src.auth.domain.exceptions import AuthenticationError, AuthorizationError, UserAlreadyExistsError
from src.auth.infrastructure.bootstrap.seed_admin import seed_admin
from src.event.api.routes import router as event_router
from src.event.domain.exceptions import (
    AlreadyParticipatingError,
    EventFullError,
    EventNotFoundError,
    EventNotUpcomingError,
    InvalidEventError,
    InvalidSessionError,
    SessionNotFoundError,
)


@asynccontextmanager
async def lifespan(_app: FastAPI) -> AsyncGenerator[None]:
    async with database.async_session_factory() as session:
        await seed_admin(session)

    yield


app = FastAPI(title="Events API", version="1.0.0", lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth_router)
app.include_router(event_router)

add_pagination(app)


@app.exception_handler(AuthenticationError)
async def authentication_error_handler(_request: Request, exc: AuthenticationError) -> JSONResponse:
    return JSONResponse(status_code=401, content={"detail": str(exc)})


@app.exception_handler(AuthorizationError)
async def authorization_error_handler(_request: Request, exc: AuthorizationError) -> JSONResponse:
    return JSONResponse(status_code=403, content={"detail": str(exc)})


@app.exception_handler(UserAlreadyExistsError)
async def user_already_exists_handler(_request: Request, exc: UserAlreadyExistsError) -> JSONResponse:
    return JSONResponse(status_code=409, content={"detail": str(exc)})


@app.exception_handler(EventNotFoundError)
async def event_not_found_handler(_request: Request, exc: EventNotFoundError) -> JSONResponse:
    return JSONResponse(status_code=404, content={"detail": str(exc)})


@app.exception_handler(InvalidEventError)
async def invalid_event_handler(_request: Request, exc: InvalidEventError) -> JSONResponse:
    return JSONResponse(status_code=422, content={"detail": str(exc)})


@app.exception_handler(SessionNotFoundError)
async def session_not_found_handler(_request: Request, exc: SessionNotFoundError) -> JSONResponse:
    return JSONResponse(status_code=404, content={"detail": str(exc)})


@app.exception_handler(InvalidSessionError)
async def invalid_session_handler(_request: Request, exc: InvalidSessionError) -> JSONResponse:
    return JSONResponse(status_code=422, content={"detail": str(exc)})


@app.exception_handler(EventFullError)
async def event_full_handler(_request: Request, exc: EventFullError) -> JSONResponse:
    return JSONResponse(status_code=409, content={"detail": str(exc)})


@app.exception_handler(EventNotUpcomingError)
async def event_not_upcoming_handler(_request: Request, exc: EventNotUpcomingError) -> JSONResponse:
    return JSONResponse(status_code=409, content={"detail": str(exc)})


@app.exception_handler(AlreadyParticipatingError)
async def already_participating_handler(_request: Request, exc: AlreadyParticipatingError) -> JSONResponse:
    return JSONResponse(status_code=409, content={"detail": str(exc)})
