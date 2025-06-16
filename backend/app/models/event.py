from app.models.models import Event 

### need to check type of start_datetime, end_datetime before using them
def create_event(db, org_id: int, category_id: int, title: str, start_datetime, end_datetime, 
                 is_all_day: bool, is_uploaded: bool, description: str = None, 
                 location: str = None, source_url: str = None, resource: str = None):
    """
    Create a new event in the database.
    Args:
        db: Database session.
        org_id: ID of the organization.
        category_id: ID of the category.
        title: Title of the event.
        description: Description of the event (optional).
        start_datetime: Start datetime of the event.
        end_datetime: End datetime of the event.
        is_all_day: Whether the event is an all-day event.
        location: Location of the event (optional).
        source_url: Source URL for the event (optional).
        resource: Resource associated with the event (optional).
        is_uploaded: Whether the event is uploaded to a third-party service.
    Returns:
        The created Event object.
    """
    event = Event(
        org_id=org_id,
        category_id=category_id,
        title=title,
        description=description,
        start_datetime=start_datetime,
        end_datetime=end_datetime,
        is_all_day=is_all_day,
        location=location,
        source_url=source_url,
        resource=resource,
        is_uploaded=is_uploaded
    )
    db.add(event)
    db.commit()
    db.refresh(event)
    return f"Event {event.id} created"

def get_event_by_id(db, event_id: int):
    """
    Retrieve an event by its ID.
    Args:
        db: Database session.
        event_id: ID of the event.
    Returns:
        The Event object if found, otherwise None.
    """
    return db.query(Event).filter(Event.id == event_id).first()
def delete_event(db, event_id: int):
    """
    Delete an event by its ID.
    Args:
        db: Database session.
        event_id: ID of the event to delete.
    Returns:
        True if the event was deleted, False if it was not found.
    """
    event = db.query(Event).filter(Event.id == event_id).first()
    if event:
        db.delete(event)
        db.commit()
        return True
    return False
def get_events_by_org(db, org_id: int):
    """
    Retrieve all events for a given organization.
    Args:
        db: Database session.
        org_id: ID of the organization.
    Returns:
        A list of Event objects.
    """
    return db.query(Event).filter(Event.org_id == org_id).all()