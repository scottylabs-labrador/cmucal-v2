from app.models.models import Career

def save_career(db, event_id: int, host: str = None, link: str = None, registration_required: bool = None):
    """
    Save a new career in the database.

    Args:
        db: Database session.
        user_id: ID of the user.
        name: Name of the career.

    Returns:
        The created Career object.
    """
    career = Career(event_id=event_id, host=host, 
                    link=link, registration_required=registration_required)
    db.add(career)
    db.commit()
    db.refresh(career)
    return f"Career {career.id} created"