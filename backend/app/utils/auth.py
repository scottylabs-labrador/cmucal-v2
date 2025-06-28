from app.services.db import SessionLocal
from app.models.models import User

def get_current_user(clerk_id: str = None):
    """
    Retrieves a user from the database based on their Clerk ID.
    Returns None if no clerk_id is provided.
    """
    db = SessionLocal()
    try:
        if not clerk_id:
            return None
        
        user = db.query(User).filter(User.clerk_id == clerk_id).first()
        return user
    finally:
        db.close() 