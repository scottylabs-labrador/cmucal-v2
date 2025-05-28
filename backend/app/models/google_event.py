# # handles DB logic
from datetime import datetime, timezone
from app.models.synced_event import SyncedEvent

def save_google_event(db, user_id, local_event_id, google_event_id, title, start, end):
    event = SyncedEvent(
        user_id=user_id,
        local_event_id=local_event_id,
        google_event_id=google_event_id,
        title=title,
        start=start,
        end=end,
        synced_at=datetime.utcnow()
    )
    db.add(event)
    db.commit()
    db.refresh(event)
    return event


def get_google_event_by_local_id(db, user_id, local_event_id):
    return db.query(SyncedEvent).filter_by(
        user_id=user_id,
        local_event_id=local_event_id
    ).first()

def delete_google_event_by_local_id(db, user_id, local_event_id):
    event = db.query(SyncedEvent).filter_by(
        user_id=user_id,
        local_event_id=local_event_id
    ).first()

    if event:
        db.delete(event)
        db.commit()
        return True  # Successfully deleted
    return False  # No matching record
