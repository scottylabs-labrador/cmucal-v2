from app.models.models import UserSavedEvent


def save_user_saved_event(db, user_id: int, event_id: int, google_event_id: str):
    """
    Save a user-saved event in the database.
    Args:
        db: Database session.
        user_id: ID of the user.
        event_id: ID of the event to be saved.
    Returns:
        The created UserSavedEvent object.
    """
    user_saved_event = UserSavedEvent(
        user_id=user_id,
        event_id=event_id,
        google_event_id=google_event_id
    )
    db.add(user_saved_event)
    db.commit()
    db.refresh(user_saved_event)
    return user_saved_event