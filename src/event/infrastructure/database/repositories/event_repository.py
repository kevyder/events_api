import uuid
from datetime import datetime
from typing import Any

from fastapi_pagination.ext.sqlmodel import apaginate
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlmodel import select as sqlmodel_select

from src.event.domain.models import Event, Session, Status
from src.event.domain.repositories import EventRepository
from src.event.infrastructure.database.models.event import EventModel
from src.event.infrastructure.database.models.session import SessionModel


class SQLAlchemyEventRepository(EventRepository):
    """Async SQLAlchemy implementation of the EventRepository."""

    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    async def list_all(self) -> Any:
        """Retrieve all events with DB-level pagination, sorted by created_at desc."""
        query = sqlmodel_select(EventModel).order_by(EventModel.created_at.desc())
        return await apaginate(
            self._session,
            query,
            transformer=lambda items: [self._to_domain(row) for row in items],
        )

    async def search_by_name(self, name: str) -> Any:
        """Search events by name with DB-level pagination, sorted by created_at desc."""
        pattern = f"%{name}%"
        query = sqlmodel_select(EventModel).where(EventModel.name.ilike(pattern)).order_by(EventModel.created_at.desc())
        return await apaginate(
            self._session,
            query,
            transformer=lambda items: [self._to_domain(row) for row in items],
        )

    async def get_by_id(self, event_id: uuid.UUID) -> Event | None:
        """Retrieve an event by ID."""
        stmt = select(EventModel).where(EventModel.id == event_id)
        result = await self._session.execute(stmt)
        row = result.scalar_one_or_none()
        if row is None:
            return None
        return self._to_domain(row)

    async def get_by_id_with_sessions(self, event_id: uuid.UUID) -> Event | None:
        """Retrieve an event with sessions in a single LEFT JOIN query."""
        stmt = (
            select(EventModel, SessionModel)
            .outerjoin(SessionModel, EventModel.id == SessionModel.event_id)
            .where(EventModel.id == event_id)
            .order_by(SessionModel.start_time.asc())
        )

        result = await self._session.execute(stmt)
        rows = result.all()
        if not rows:
            return None

        event = self._to_domain(rows[0][0])
        event.sessions = [self._to_session_domain(row[1]) for row in rows if row[1] is not None]
        return event

    async def list_sessions_by_event(self, event_id: uuid.UUID) -> list[Session]:
        """Retrieve all sessions for an event ordered by start time ascending."""
        stmt = select(SessionModel).where(SessionModel.event_id == event_id).order_by(SessionModel.start_time.asc())
        result = await self._session.execute(stmt)
        rows = result.scalars().all()
        return [self._to_session_domain(row) for row in rows]

    async def get_session_by_id(self, event_id: uuid.UUID, session_id: uuid.UUID) -> Session | None:
        """Retrieve a session by event and session IDs."""
        stmt = select(SessionModel).where(SessionModel.event_id == event_id, SessionModel.id == session_id)
        result = await self._session.execute(stmt)
        row = result.scalar_one_or_none()
        if row is None:
            return None
        return self._to_session_domain(row)

    async def create_session(self, session: Session) -> Session:
        """Persist a new session."""
        model = SessionModel(
            id=session.id,
            event_id=session.event_id,
            title=session.title,
            speaker=session.speaker,
            start_time=session.start_time,
            end_time=session.end_time,
            created_at=session.created_at,
            updated_at=session.updated_at,
        )
        self._session.add(model)
        await self._session.commit()
        await self._session.refresh(model)
        return self._to_session_domain(model)

    async def update_session(self, session: Session) -> Session:
        """Update an existing session."""
        stmt = select(SessionModel).where(SessionModel.event_id == session.event_id, SessionModel.id == session.id)
        result = await self._session.execute(stmt)
        model = result.scalar_one_or_none()
        if model is None:
            return session

        model.title = session.title
        model.speaker = session.speaker
        model.start_time = session.start_time
        model.end_time = session.end_time
        model.updated_at = datetime.now()

        await self._session.commit()
        await self._session.refresh(model)
        return self._to_session_domain(model)

    async def delete_session(self, event_id: uuid.UUID, session_id: uuid.UUID) -> None:
        """Delete a session by event and session IDs."""
        stmt = select(SessionModel).where(SessionModel.event_id == event_id, SessionModel.id == session_id)
        result = await self._session.execute(stmt)
        model = result.scalar_one_or_none()
        if model is not None:
            await self._session.delete(model)
            await self._session.commit()

    async def create(self, event: Event) -> Event:
        """Persist a new event."""
        model = EventModel(
            id=event.id,
            name=event.name,
            description=event.description,
            start_date=event.start_date,
            end_date=event.end_date,
            capacity=event.capacity,
            status=event.status.value,
            created_at=event.created_at,
            updated_at=event.updated_at,
        )
        self._session.add(model)
        await self._session.commit()
        await self._session.refresh(model)
        return self._to_domain(model)

    async def update(self, event: Event) -> Event:
        """Update an existing event."""
        stmt = select(EventModel).where(EventModel.id == event.id)
        result = await self._session.execute(stmt)
        model = result.scalar_one_or_none()
        if model is None:
            return event

        model.name = event.name
        model.description = event.description
        model.start_date = event.start_date
        model.end_date = event.end_date
        model.capacity = event.capacity
        model.status = event.status.value
        model.updated_at = datetime.now()

        await self._session.commit()
        await self._session.refresh(model)
        return self._to_domain(model)

    async def delete(self, event_id: uuid.UUID) -> None:
        """Delete an event by ID."""
        session_stmt = select(SessionModel).where(SessionModel.event_id == event_id)
        session_result = await self._session.execute(session_stmt)
        for session_model in session_result.scalars().all():
            await self._session.delete(session_model)

        stmt = select(EventModel).where(EventModel.id == event_id)
        result = await self._session.execute(stmt)
        model = result.scalar_one_or_none()
        if model is not None:
            await self._session.delete(model)
            await self._session.commit()

    @staticmethod
    def _to_domain(model: EventModel) -> Event:
        """Map a SQLAlchemy model to a domain entity."""
        return Event.model_construct(
            id=model.id,
            name=model.name,
            description=model.description,
            start_date=model.start_date,
            end_date=model.end_date,
            capacity=model.capacity,
            status=Status(model.status),
            created_at=model.created_at,
            updated_at=model.updated_at,
        )

    @staticmethod
    def _to_session_domain(model: SessionModel) -> Session:
        """Map a SQLAlchemy model to a session domain entity."""
        return Session.model_construct(
            id=model.id,
            event_id=model.event_id,
            title=model.title,
            speaker=model.speaker,
            start_time=model.start_time,
            end_time=model.end_time,
            created_at=model.created_at,
            updated_at=model.updated_at,
        )
