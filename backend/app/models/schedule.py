from app.models.models import Schedule

def create_schedule(db, user_id: int, name: str):
    """
    Create a new schedule in the database.
    
    Args:
        db: Database session.
        user_id: ID of the user.
        name: Name of the schedule.
        
    Returns:
        The created Schedule object.
    """
    schedule = Schedule(user_id=user_id, name=name)
    db.add(schedule)
    db.commit()
    db.refresh(schedule)
    return schedule