import uuid
from datetime import datetime
from typing import Any

from fastapi_pagination.ext.sqlmodel import apaginate
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlmodel import select as sqlmodel_select

from src.event.domain.models import Event, Status
from src.event.domain.repositories import EventRepository
from src.event.infrastructure.database.models.event import EventModel


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
