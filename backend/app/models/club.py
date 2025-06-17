from app.models.models import Club

def save_club(db, event_id: int):
    """
    Create a new club in the database.

    Args:
        db: Database session.
        name: Name of the club.
        description: Description of the club.
        org_id: ID of the organization to which the club belongs.

    Returns:
        The created Club object.
    """
    club = Club(event_id=event_id)
    db.add(club)
    db.flush()  
    db.refresh(club)
    return f"Club event {event_id} created"