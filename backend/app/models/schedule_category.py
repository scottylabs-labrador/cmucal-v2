from app.models.models import ScheduleCategory

def create_schedule_category(db, schedule_id: int, category_id: int):
    """
    Save a user-saved category in the database.

    Args:
        db: Database session.
        user_id: ID of the user.
        category_id: ID of the category to be saved.

    Returns:
        The created UserSavedCategory object.
    """
    schedule_category = ScheduleCategory(
        schedule_id=schedule_id,
        category_id=category_id
    )
    db.add(schedule_category)
    db.commit()
    db.refresh(schedule_category)
    return schedule_category