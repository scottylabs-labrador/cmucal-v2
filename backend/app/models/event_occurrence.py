from app.models.models import (
    Event, RecurrenceRule, EventOccurrence,
    RecurrenceExdate, RecurrenceRdate, EventOverride
)
from app.models.enums import RecurrenceType
from app.models.recurrence_rule import get_rrule_from_db_rule
from datetime import datetime, timedelta, timezone
from typing import List
from copy import deepcopy
from app.utils.date import _ensure_aware, _parse_iso_aware


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
    start_dt = _parse_iso_aware(start_datetime) if isinstance(start_datetime, str) else start_datetime
    end_dt   = _parse_iso_aware(end_datetime)   if isinstance(end_datetime, str)   else end_datetime
    saved_at = _parse_iso_aware(event_saved_at) if isinstance(event_saved_at, str) else event_saved_at

    event_occurrence = EventOccurrence(
        event_id=event_id,
        org_id=org_id,
        category_id=category_id,
        title=title,
        start_datetime=start_dt,
        end_datetime=end_dt,
        event_saved_at=saved_at,
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
    # Defensive duration (end could be equal to start in some feeds)
    end_datetime = _parse_iso_aware(event.end_datetime) if event.end_datetime else None
    start_datetime = _parse_iso_aware(event.start_datetime) if event.start_datetime else None
    duration = (end_datetime or start_datetime) - start_datetime
    if duration.total_seconds() < 0:
        duration = timedelta(0)

    now_utc = datetime.now(timezone.utc)
    six_months_later = now_utc + timedelta(days=180)

    temp_rule = rule # Create a copy of the rule to avoid modifying the original

    # ---- Safe copy of rule “view” for expansion window
    temp_rule = deepcopy(rule)
    # until logic
    if not temp_rule.count:
        if not temp_rule.until:
            temp_rule.until = six_months_later
        else:
            # both aware
            temp_rule.until = min(_ensure_aware(temp_rule.until), six_months_later)



    print("➡️ rule.start_datetime =", rule.start_datetime)
    print("➡️ rule.until =", rule.until)
    print("➡️ temp_rule.until =", temp_rule.until)

    # Build an rrule iterator from temp_rule
    rrule_iter = get_rrule_from_db_rule(temp_rule)

    # Pull EXDATE/RDATE/Overrides
    exdates = {
        _ensure_aware(x.exdate) for x in db.query(RecurrenceExdate)
            .filter_by(rrule_id=rule.id).all()
    }
    rdates = {
        _ensure_aware(x.rdate) for x in db.query(RecurrenceRdate)
            .filter_by(rrule_id=rule.id).all()
    }
    overrides = {
        _ensure_aware(o.recurrence_date): o
        for o in db.query(EventOverride).filter_by(rrule_id=rule.id).all()
    }

    # Start fresh for this event’s occurrences
    db.query(EventOccurrence).filter_by(event_id=event.id).delete(synchronize_session=False)

    count = 0
    seen_starts = set()  # to avoid dupes when RDATE == RRULE date

    # 1) Generate from RRULE, skipping EXDATE and applying overrides
    for occ_start in rrule_iter:
        occ_start = _ensure_aware(occ_start)
        if occ_start in exdates:
            continue

        if occ_start in overrides:
            o = overrides[occ_start]
            start_dt = o.new_start or occ_start
            end_dt   = o.new_end   or (start_dt + duration)
            title    = o.new_title or event.title
            desc     = o.new_description if o.new_description is not None else event.description
            loc      = o.new_location if o.new_location is not None else event.location
        else:
            start_dt = occ_start
            end_dt   = occ_start + duration
            title    = event.title
            desc     = event.description
            loc      = event.location# 1) Generate from RRULE, skipping EXDATE and applying overrides

        db.add(EventOccurrence(
            event_id=event.id,
            org_id=event.org_id,
            category_id=event.category_id,
            title=title,
            start_datetime=start_dt,
            end_datetime=end_dt,
            event_saved_at=event.last_updated_at,
            recurrence="RECURRING",
            is_all_day=event.is_all_day,
            user_edited=event.user_edited,
            description=desc,
            location=loc,
            source_url=event.source_url,
        ))
        seen_starts.add(start_dt)
        count += 1
    
    # 2) Add RDATEs that weren’t already covered
    for rdate in sorted(rdates):
        # Skip if excluded or already added from RRULE/override
        if rdate in exdates or rdate in seen_starts:
            continue

        # If there is an override on this rdate, apply it
        if rdate in overrides:
            o = overrides[rdate]
            start_dt = o.new_start or rdate
            end_dt   = o.new_end   or (start_dt + duration)
            title    = o.new_title or event.title
            desc     = o.new_description if o.new_description is not None else event.description
            loc      = o.new_location if o.new_location is not None else event.location
        else:
            start_dt = rdate
            end_dt   = rdate + duration
            title    = event.title
            desc     = event.description
            loc      = event.location

        # (Optional) Respect the same 6-month cap when no count/until
        if not rule.count and (start_dt > six_months_later):
            continue

        db.add(EventOccurrence(
            event_id=event.id,
            org_id=event.org_id,
            category_id=event.category_id,
            title=title,
            start_datetime=start_dt,
            end_datetime=end_dt,
            event_saved_at=event.last_updated_at,
            recurrence="RECURRING",
            is_all_day=event.is_all_day,
            user_edited=event.user_edited,
            description=desc,
            location=loc,
            source_url=event.source_url,
        ))
        count += 1

    db.flush()
    return f"Populated {count} occurrences for event {event.id}"