from app.models.models import EventTag

def save_event_tag(db, event_id: int, tag_id: int):
    """
    Save a tag associated with an event in the database.

    Args:
        db: Database session.
        event_id: ID of the event.
        tag_id: ID of the tag to be saved.

    Returns:
        The created EventTag object.
    """
    event_tag = EventTag(
        event_id=event_id,
        tag_id=tag_id
    )
    db.add(event_tag)
    db.commit()
    db.refresh(event_tag)
    return f"Event tag (event_id: {event_id}, tag_id: {tag_id}) created"