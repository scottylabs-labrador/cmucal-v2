from sqlalchemy import Column, String, DateTime, BigInteger, ForeignKey
from app.services.db import Base  # Adjust import path
from datetime import datetime

class SyncedEvent(Base):
    __tablename__ = "synced_events"

    id = Column(BigInteger, primary_key=True, autoincrement=True)
    local_event_id = Column(String, nullable=False)
    google_event_id = Column(String, nullable=False)
    title = Column(String, nullable=True)
    start = Column(String, nullable=False)   # stored as TEXT in Supabase
    end = Column(String, nullable=True)     # stored as TEXT in Supabase
    synced_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    user_id = Column(BigInteger, ForeignKey("users.id"), nullable=False)
