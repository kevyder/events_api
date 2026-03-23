from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from src.database import get_async_session
from src.event.infrastructure.database.repositories.event_repository import SQLAlchemyEventRepository
from src.event.use_cases.create_event import CreateEvent
from src.event.use_cases.create_session import CreateSession
from src.event.use_cases.delete_event import DeleteEvent
from src.event.use_cases.delete_session import DeleteSession
from src.event.use_cases.get_event import GetEvent
from src.event.use_cases.leave_event import LeaveEvent
from src.event.use_cases.list_events import ListEvents
from src.event.use_cases.list_my_events import ListMyEvents
from src.event.use_cases.participate_in_event import ParticipateInEvent
from src.event.use_cases.search_events import SearchEvents
from src.event.use_cases.update_event import UpdateEvent
from src.event.use_cases.update_session import UpdateSession


def get_list_events(session: AsyncSession = Depends(get_async_session)) -> ListEvents:
    """Inject a ListEvents use case."""
    return ListEvents(SQLAlchemyEventRepository(session))


def get_get_event(session: AsyncSession = Depends(get_async_session)) -> GetEvent:
    """Inject a GetEvent use case."""
    return GetEvent(SQLAlchemyEventRepository(session))


def get_search_events(session: AsyncSession = Depends(get_async_session)) -> SearchEvents:
    """Inject a SearchEvents use case."""
    return SearchEvents(SQLAlchemyEventRepository(session))


def get_create_event(session: AsyncSession = Depends(get_async_session)) -> CreateEvent:
    """Inject a CreateEvent use case."""
    return CreateEvent(SQLAlchemyEventRepository(session))


def get_create_session(session: AsyncSession = Depends(get_async_session)) -> CreateSession:
    """Inject a CreateSession use case."""
    return CreateSession(SQLAlchemyEventRepository(session))


def get_update_event(session: AsyncSession = Depends(get_async_session)) -> UpdateEvent:
    """Inject an UpdateEvent use case."""
    return UpdateEvent(SQLAlchemyEventRepository(session))


def get_update_session(session: AsyncSession = Depends(get_async_session)) -> UpdateSession:
    """Inject an UpdateSession use case."""
    return UpdateSession(SQLAlchemyEventRepository(session))


def get_delete_event(session: AsyncSession = Depends(get_async_session)) -> DeleteEvent:
    """Inject a DeleteEvent use case."""
    return DeleteEvent(SQLAlchemyEventRepository(session))


def get_delete_session(session: AsyncSession = Depends(get_async_session)) -> DeleteSession:
    """Inject a DeleteSession use case."""
    return DeleteSession(SQLAlchemyEventRepository(session))


def get_participate_in_event(session: AsyncSession = Depends(get_async_session)) -> ParticipateInEvent:
    """Inject a ParticipateInEvent use case."""
    return ParticipateInEvent(SQLAlchemyEventRepository(session))


def get_leave_event(session: AsyncSession = Depends(get_async_session)) -> LeaveEvent:
    """Inject a LeaveEvent use case."""
    return LeaveEvent(SQLAlchemyEventRepository(session))


def get_list_my_events(session: AsyncSession = Depends(get_async_session)) -> ListMyEvents:
    """Inject a ListMyEvents use case."""
    return ListMyEvents(SQLAlchemyEventRepository(session))
