from app.models.models import EventOccurrence, RecurrenceRule, Event
from app.models.enums import RecurrenceType
from app.models.recurrence_rule import get_rrule_from_db_rule
from datetime import datetime, timedelta, timezone
from typing import List
import copy

### need to check type of event_saved_at, start_datetime, end_datetime before using them
def save_event_occurrence(db, event_id: int, org_id: int, category_id: int, title: str, 
                          start_datetime, end_datetime, recurrence: RecurrenceType,
                          event_saved_at: str, 
                          is_all_day: bool, user_edited: List[int], description: str = None, 
                          location: str = None, source_url: str = None):
    """
    Save an event occurrence in the database.

    Args:
        db: Database session.
        event_id: ID of the event.
        start_time: Start time of the occurrence in ISO format.
        end_time: End time of the occurrence in ISO format.

    Returns:
        The created EventOccurrence object.
    """
    event_occurrence = EventOccurrence(
        event_id=event_id,
        org_id=org_id,
        category_id=category_id,
        title=title,
        start_datetime=start_datetime,
        end_datetime=end_datetime,
        event_saved_at=event_saved_at,
        recurrence=recurrence,
        is_all_day=is_all_day,
        user_edited=user_edited,
        description=description,
        location=location,
        source_url=source_url)
    db.add(event_occurrence)
    db.flush()
    db.refresh(event_occurrence)
    return event_occurrence


def populate_event_occurrences(db, event: Event, rule: RecurrenceRule):
    """
    Populate occurrences for a recurring event based on the recurrence rule.
    If count is set, respects the count -> No limit from until or 6-month cap.
    If count is not set and until is set, respects the until date with a 6-month cap, and stores the orig until date in the rule. (see add_recurrence_rule)
    If both count and until are not set, uses a 6-month cap from now, and stores the orig until date in the rule. (see add_recurrence_rule)
    Args:
        db: Database session.
        event: The Event object for which occurrences are to be populated.
        rule: The RecurrenceRule object defining the recurrence pattern.
    Returns:
        A message indicating the number of occurrences populated.
    """
    count = 0
    duration = event.end_datetime - event.start_datetime
    six_months_later = datetime.now(timezone.utc) + timedelta(days=180)

    temp_rule = rule # Create a copy of the rule to avoid modifying the original

    # ✅ Fallback for `until`
    if not rule.count:
        if not rule.until:
            temp_rule.until = six_months_later
        else:
            # ❗ make sure both are timezone-aware
            temp_rule.until = min(rule.until, six_months_later)

    print("➡️ rule.start_datetime =", rule.start_datetime)
    print("➡️ rule.until =", rule.until)
    print("➡️ temp_rule.until =", temp_rule.until)

    rrule = get_rrule_from_db_rule(temp_rule)
    print("➡️ FIRST OCCURRENCE:", next(iter(rrule), "None"))

    for occ_start in rrule:
        occ_end = occ_start + duration

        occurrence = EventOccurrence(
            event_id=event.id,
            org_id=event.org_id,
            category_id=event.category_id,
            title=event.title,
            start_datetime=occ_start,
            end_datetime=occ_end,
            event_saved_at=event.last_updated_at,
            recurrence="RECURRING",
            is_all_day=event.is_all_day,
            user_edited=event.user_edited,
            description=event.description,
            location=event.location,
            source_url=event.source_url,
        )
        db.add(occurrence)
        count += 1

    db.flush()
    return f"Populated {count} occurrences for event {event.id}"
