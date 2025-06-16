from app.models.models import EventOccurrence
from app.models.enums import RecurrenceType

### need to check type of event_saved_at, start_datetime, end_datetime before using them
def save_event_occurrence(db, event_id: int, org_id: int, category_id: int, title: str, 
                          start_datetime, end_datetime, recurrence: RecurrenceType,
                          event_saved_at,
                          is_all_day: bool, is_uploaded: bool, description: str = None, 
                          location: str = None, source_url: str = None, resource: str = None):
    """
    Save an event occurrence in the database.

    Args:
        db: Database session.
        event_id: ID of the event.
        start_time: Start time of the occurrence in ISO format.
        end_time: End time of the occurrence in ISO format.

    Returns:
        The created EventOccurrence object.
    """
    event_occurrence = EventOccurrence(
        event_id=event_id,
        org_id=org_id,
        category_id=category_id,
        title=title,
        start_datetime=start_datetime,
        end_datetime=end_datetime,
        event_saved_at=event_saved_at,
        recurrence=recurrence,
        is_all_day=is_all_day,
        is_uploaded=is_uploaded,
        description=description,
        location=location,
        source_url=source_url,
        resource=resource
    )
    db.add(event_occurrence)
    db.commit()
    db.refresh(event_occurrence)
    return f"Event occurrence (event_id: {event_id}, start_time: {start_datetime}, end_time: {end_datetime}) created"