import uuid

from fastapi import APIRouter, Depends, Query
from fastapi_pagination import Page

from src.auth.api.dependencies import require_role
from src.auth.domain.models import User
from src.event.api.dependencies import (
    get_create_event,
    get_delete_event,
    get_get_event,
    get_list_events,
    get_search_events,
    get_update_event,
)
from src.event.api.schemas import EventCreateRequest, EventResponse, EventUpdateRequest
from src.event.domain.models import Event
from src.event.use_cases.create_event import CreateEvent
from src.event.use_cases.delete_event import DeleteEvent
from src.event.use_cases.get_event import GetEvent
from src.event.use_cases.list_events import ListEvents
from src.event.use_cases.search_events import SearchEvents
from src.event.use_cases.update_event import _UNSET, UpdateEvent

router = APIRouter(prefix="/events", tags=["events"])


def _to_response(event: Event) -> EventResponse:
    """Map a domain Event to an API response."""
    return EventResponse(
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


@router.get("", response_model=Page[EventResponse])
async def list_events(use_case: ListEvents = Depends(get_list_events)):
    """List events with pagination. Open to everyone."""
    return await use_case.execute()


@router.get("/search", response_model=Page[EventResponse])
async def search_events(
    name: str = Query(..., min_length=1),
    use_case: SearchEvents = Depends(get_search_events),
):
    """Search events by name using a SQL LIKE query. Open to everyone."""
    return await use_case.execute(name)


@router.get("/{event_id}", response_model=EventResponse)
async def get_event(event_id: uuid.UUID, use_case: GetEvent = Depends(get_get_event)):
    """Get a single event by ID. Open to everyone."""
    event = await use_case.execute(event_id)
    return _to_response(event)


@router.post("", response_model=EventResponse, status_code=201)
async def create_event(
    body: EventCreateRequest,
    use_case: CreateEvent = Depends(get_create_event),
    current_user: User = Depends(require_role("admin")),
):
    """Create a new event. Admin only."""
    event = await use_case.execute(
        name=body.name,
        description=body.description,
        start_date=body.start_date,
        end_date=body.end_date,
        capacity=body.capacity,
    )
    return _to_response(event)


@router.patch("/{event_id}", response_model=EventResponse)
async def update_event(
    event_id: uuid.UUID,
    body: EventUpdateRequest,
    use_case: UpdateEvent = Depends(get_update_event),
    current_user: User = Depends(require_role("admin")),
):
    """Partially update an event. Admin only."""
    # Build kwargs only for fields that were explicitly provided in the request body
    kwargs: dict = {}
    provided = body.model_fields_set

    if "name" in provided:
        kwargs["name"] = body.name
    if "description" in provided:
        kwargs["description"] = body.description
    else:
        kwargs["description"] = _UNSET
    if "start_date" in provided:
        kwargs["start_date"] = body.start_date
    if "end_date" in provided:
        kwargs["end_date"] = body.end_date
    if "capacity" in provided:
        kwargs["capacity"] = body.capacity
    if "status" in provided:
        kwargs["status"] = body.status

    event = await use_case.execute(event_id=event_id, **kwargs)
    return _to_response(event)


@router.delete("/{event_id}", status_code=200)
async def delete_event(
    event_id: uuid.UUID,
    use_case: DeleteEvent = Depends(get_delete_event),
    current_user: User = Depends(require_role("admin")),
):
    """Delete an event. Admin only."""
    await use_case.execute(event_id)

    return "Event deleted successfully."
