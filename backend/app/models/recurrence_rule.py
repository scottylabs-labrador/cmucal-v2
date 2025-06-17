from app.models.models import RecurrenceRule
from app.models.enums import FrequencyType, DayType
from typing import List
from datetime import date

def save_recurrence_rule(db, rule: RecurrenceRule):
    """
    Save a recurrence rule in the database.

    Args:
        db: Database session.
        rule: RecurrenceRule object to be saved.

    Returns:
        The created RecurrenceRule object.
    """
    db.add(rule)
    db.commit()
    db.refresh(rule)
    return rule

def add_recurrence_rule(db, frequency: FrequencyType = None, interval: int = None, 
                        count: int = None, until: str = None, event_id: int = None, 
                        by_month: int = None, by_month_day: int = None, by_day: List[str] = None):
    new_rule = RecurrenceRule(
        frequency=frequency,
        interval=interval,
        count=count,
        until=date(until),
        event_id=event_id,  # replace with actual event ID
        by_month=by_month,
        by_month_day=by_month_day,
        by_day=by_day
    )

    db.session.add(new_rule)
    db.session.commit()
    return f"Recurrence rule {new_rule.id} created"