from app.models.models import Academic
from typing import List

def save_academic(db, event_id: int, course_num: str, course_name: str, instructors: List[str] = None):
    """
    Create a new academic record in the database.

    Args:
        db: Database session.
        user_id: ID of the user.
        name: Name of the academic record.

    Returns:
        The created Academic object.
    """
    academic = Academic(event_id=event_id, course_num=course_num, 
                        course_name=course_name, instructors=instructors)
    db.add(academic)
    db.commit()
    db.refresh(academic)
    return f"Academic {academic.id} created"