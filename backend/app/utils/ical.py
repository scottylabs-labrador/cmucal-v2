from icalendar import Calendar
from recurring_ical_events import recurring_ical_events
from datetime import datetime, timedelta, timezone, date
from typing import Dict, List, Optional
import requests

from app.models.models import (
    Event, RecurrenceRule, EventOccurrence,
    RecurrenceExdate, RecurrenceRdate, EventOverride
)
from app.models.recurrence_rule import add_recurrence_rule
from app.models.event_occurrence import populate_event_occurrences, save_event_occurrence
from app.models.event import save_event

# Your existing helpers from the /create_event flow:
# save_event, save_event_occurrence, add_recurrence_rule, populate_event_occurrences
# (plus any type-specific helpers like save_career/save_academic if you want to map fields)

LOOKAHEAD_DAYS = 180  # window for generating occurrences

def import_ical_feed_using_helpers(
    db_session,
    ical_text_or_url: str,
    *,
    org_id: int,
    category_id: int,
    default_event_type: Optional[str] = None,   # e.g. "CLUB"/"ACADEMIC"/"CAREER"/None
    source_url: Optional[str] = None,
    user_edited: Optional[bool] = False,
    delete_missing_uids: bool = False           # if True, remove events that disappeared from feed
):
    """
    Parse an ICS (string or URL), group by UID, and upsert events using the same logic
    as /create_event. All datetimes passed to helpers as ISO strings.
    """
    # 1) Load ICS (support webcal:// or https:// or raw text)
    ical_text = _fetch_ics_text(ical_text_or_url)

    cal = Calendar.from_ical(ical_text)

    # 2) Group VEVENTs by UID
    by_uid: Dict[str, List] = {}
    for comp in cal.walk():
        if comp.name != "VEVENT":
            continue
        uid = str(comp.get("UID") or "").strip()
        if not uid:
            continue
        by_uid.setdefault(uid, []).append(comp)

    incoming_uids = set(by_uid.keys())

    now = datetime.now(timezone.utc)
    horizon = now + timedelta(days=LOOKAHEAD_DAYS)

    # 3) Process each UID group
    for uid, components in by_uid.items():
        _process_uid_group_with_helpers(
            db_session=db_session,
            uid=uid,
            components=components,
            now=now,
            horizon=horizon,
            org_id=org_id,
            category_id=category_id,
            default_event_type=default_event_type,
            source_url=source_url,
            user_edited=user_edited
        )

    # 4) Optionally delete events no longer present
    if delete_missing_uids:
        existing_uids = {row[0] for row in db_session.query(Event.ical_uid).filter(Event.org_id==org_id, Event.category_id==category_id).all()}
        missing = list(existing_uids - incoming_uids)
        if missing:
            db_session.query(Event).filter(Event.ical_uid.in_(missing)).delete(synchronize_session=False)

    db_session.commit()


def _process_uid_group_with_helpers(
    db_session,
    uid: str,
    components: List,
    now: datetime,
    horizon: datetime,
    *,
    org_id: int,
    category_id: int,
    default_event_type: Optional[str],
    source_url: Optional[str],
    user_edited: Optional[bool]
):
    # Split: base components (no RECURRENCE-ID) vs overrides
    base_candidates = [c for c in components if not c.get("RECURRENCE-ID")]
    override_components = [c for c in components if c.get("RECURRENCE-ID")]

    if not base_candidates:
        return

    base = _pick_base_component(base_candidates)

    # Base fields
    dtstart = _decoded_dt(base, "DTSTART")  # aware datetime or date
    dtend   = _decoded_dt(base, "DTEND")
    is_all_day = _is_all_day_component(base)

    # Convert to ISO strings for your helper
    start_iso = _to_iso_for_helper(dtstart, is_all_day)
    end_iso   = _to_iso_for_helper(dtend,   is_all_day) if dtend else start_iso

    title = str(base.get("SUMMARY") or "").strip()
    description = str(base.get("DESCRIPTION") or "").strip()
    location = str(base.get("LOCATION") or "").strip()

    seq = int(base.get("SEQUENCE", 0) or 0)
    lm  = base.get("LAST-MODIFIED")
    last_modified = lm.dt if lm else None
    last_modified_iso = _to_iso_for_helper(last_modified, False) if last_modified else None

    # Upsert the Event by UID (using your helper flow)
    # We mirror the /create_event argument structure and then set iCal metadata after flush.
    existing = Event.query.filter_by(ical_uid=uid).first()
    if existing:
        # Decide if we should update (SEQUENCE or LAST-MODIFIED newer)
        should_update = (
            seq > (existing.ical_sequence or 0) or
            (last_modified and (existing.ical_last_modified is None or last_modified > existing.ical_last_modified))
        )
        if should_update:
            # Reuse your helper path: save_event is likely for new; for updates we set fields directly.
            existing.title = title
            existing.description = description or None
            existing.location = location or None
            existing.start_datetime = _ensure_aware(dtstart)
            existing.end_datetime = _ensure_aware(dtend) if dtend else _ensure_aware(dtstart)
            existing.is_all_day = is_all_day
            existing.source_url = source_url
            existing.event_type = default_event_type
            existing.user_edited = user_edited
            existing.org_id = org_id
            existing.category_id = category_id
            existing.ical_sequence = seq
            if last_modified:
                existing.ical_last_modified = _ensure_aware(last_modified)
            db_session.flush()
            event = existing
        else:
            event = existing
    else:
        # Create via your helper (expects ISO strings)
        event = save_event(
            db_session,
            org_id=org_id,
            category_id=category_id,
            title=title,
            description=description or None,
            start_datetime=start_iso,
            end_datetime=end_iso,
            is_all_day=is_all_day,
            location=location or None,
            source_url=source_url,
            event_type=default_event_type,
            user_edited=user_edited
        )
        db_session.flush()
        # Add iCal metadata directly on the persisted model
        event.ical_uid = uid
        event.ical_sequence = seq
        if last_modified:
            event.ical_last_modified = _ensure_aware(last_modified)
        db_session.flush()

    # Handle recurrence rule (RRULE) + EXDATE + RDATE
    rrule = base.get("RRULE")
    rule: Optional[RecurrenceRule] = None

    if rrule:
        # Prepare recurrence_data for your helper
        # NOTE: all datetimes passed as ISO
        until_val = (rrule.get("UNTIL") or [None])[0]
        # icalendar may give UNTIL as date/datetime; convert to ISO string if present
        until_iso = _to_iso_for_helper(until_val, _looks_like_date(until_val)) if until_val else None

        recurrence_data = {
            "frequency": (rrule.get("FREQ") or [None])[0],
            "interval":  (rrule.get("INTERVAL") or [1])[0],
            "start_datetime": start_iso,
            "count":     (rrule.get("COUNT") or [None])[0],
            "until":     until_iso,
            "by_day":    ",".join(rrule.get("BYDAY") or []),
            "by_month_day": (rrule.get("BYMONTHDAY") or [None])[0],
            "by_month":     (rrule.get("BYMONTH") or [None])[0],
        }

        # Upsert rule using your helper
        existing_rule = RecurrenceRule.query.filter_by(event_id=event.id).first()
        if existing_rule:
            # Update in place to mirror add_recurrence_rule behavior
            existing_rule.frequency = recurrence_data["frequency"]
            existing_rule.interval = recurrence_data["interval"]
            existing_rule.count = recurrence_data["count"]
            existing_rule.until = _parse_iso(until_iso) if until_iso else None
            existing_rule.by_day = recurrence_data["by_day"] or None
            existing_rule.by_month_day = recurrence_data["by_month_day"]
            existing_rule.by_month = recurrence_data["by_month"]
            existing_rule.start_datetime = _parse_iso(start_iso)
            db_session.flush()
            rule = existing_rule
        else:
            rule = add_recurrence_rule(
                db_session,
                event_id=event.id,
                frequency=recurrence_data["frequency"],
                interval=recurrence_data["interval"],
                start_datetime=recurrence_data["start_datetime"],  # ISO
                count=recurrence_data["count"],
                until=recurrence_data["until"],                    # ISO or None
                by_day=recurrence_data["by_day"],
                by_month_day=recurrence_data["by_month_day"],
                by_month=recurrence_data["by_month"],
            )
            db_session.flush()

        # Refresh EXDATEs / RDATEs idempotently
        RecurrenceExdate.query.filter_by(recurrence_id=rule.id).delete(synchronize_session=False)
        RecurrenceRdate.query.filter_by(recurrence_id=rule.id).delete(synchronize_session=False)

        for ex in base.get("EXDATE", []):
            for exdate in ex.dts:
                db_session.add(RecurrenceExdate(
                    recurrence_id=rule.id,
                    exdate=_ensure_aware(exdate.dt)
                ))

        for r in base.get("RDATE", []):
            for rdate in r.dts:
                db_session.add(RecurrenceRdate(
                    recurrence_id=rule.id,
                    rdate=_ensure_aware(rdate.dt)
                ))
        db_session.flush()

        # Store overrides for this UID (RECURRENCE-ID)
        EventOverride.query.filter_by(recurrence_id=rule.id).delete(synchronize_session=False)
        for oc in override_components:
            rid = oc.get("RECURRENCE-ID")
            if not rid:
                continue
            db_session.add(EventOverride(
                recurrence_id=rule.id,
                recurrence_date=_ensure_aware(rid.dt),
                new_start=_decoded_dt(oc, "DTSTART"),
                new_end=_decoded_dt(oc, "DTEND"),
                new_title=str(oc.get("SUMMARY") or None),
                new_description=str(oc.get("DESCRIPTION") or None),
                new_location=str(oc.get("LOCATION") or None),
            ))
        db_session.flush()

        # Regenerate occurrences using your helper
        # (Assumes populate_event_occurrences reads rule + exdates/rdates/overrides)
        populate_event_occurrences(db_session, event=event, rule=rule)

    else:
        # One-time event: clean any previous rule + just write one occurrence
        old_rule = RecurrenceRule.query.filter_by(event_id=event.id).first()
        if old_rule:
            RecurrenceExdate.query.filter_by(recurrence_id=old_rule.id).delete(synchronize_session=False)
            RecurrenceRdate.query.filter_by(recurrence_id=old_rule.id).delete(synchronize_session=False)
            # If you set ON DELETE CASCADE for overrides linked to rule, this single delete is enough:
            db_session.delete(old_rule)
            db_session.flush()

        # Write a single occurrence via your helper
        event_saved_at = getattr(event, "last_updated_at", datetime.utcnow())
        save_event_occurrence(
            db_session,
            event_id=event.id,
            org_id=org_id,
            category_id=category_id,
            title=title,
            start_datetime=start_iso,  # ISO
            end_datetime=end_iso,      # ISO
            recurrence="ONETIME",
            event_saved_at=event_saved_at,
            is_all_day=is_all_day,
            user_edited=user_edited,
            description=description or None,
            location=location or None,
            source_url=source_url
        )

    # Optional: if you want occurrences only up to `horizon`, keep your populate logic bounded by a horizon.


# -----------------------
# Utilities
# -----------------------

def _fetch_ics_text(ical_text_or_url: str) -> str:
    s = ical_text_or_url.strip()
    if s.startswith(("http://", "https://", "webcal://")):
        if s.startswith("webcal://"):
            s = "https://" + s[len("webcal://"):]
        r = requests.get(s, timeout=30)
        r.raise_for_status()
        return r.text
    return s  # already raw ICS text

def _decoded_dt(component, key: str):
    """Return a timezone-aware datetime if present; if a DATE-only, convert to midnight UTC."""
    if not component.get(key):
        return None
    val = component.decoded(key)
    # val can be date or datetime
    if isinstance(val, date) and not isinstance(val, datetime):
        # All-day date → normalize to midnight UTC
        return datetime(val.year, val.month, val.day, tzinfo=timezone.utc)
    # Ensure tz-aware
    return _ensure_aware(val)

def _ensure_aware(dt):
    if dt is None:
        return None
    if isinstance(dt, date) and not isinstance(dt, datetime):
        dt = datetime(dt.year, dt.month, dt.day)
    if dt.tzinfo is None:
        return dt.replace(tzinfo=timezone.utc)
    return dt

def _to_iso_for_helper(dt, is_all_day: bool) -> str:
    """
    Convert datetime to ISO string for helper. If all-day and time is midnight, keep date part normalized.
    """
    if dt is None:
        return None
    dt = _ensure_aware(dt)
    # Keep full ISO; your helpers accept ISO strings
    return dt.isoformat()

def _is_all_day_component(component) -> bool:
    # VALUE=DATE → all-day; or DTSTART was a date (handled above)
    dtstart = component.get("DTSTART")
    if not dtstart:
        return False
    params = getattr(dtstart, "params", {})
    return params.get("VALUE") == "DATE"

def _looks_like_date(val) -> bool:
    return isinstance(val, date) and not isinstance(val, datetime)

def _parse_iso(iso_str: Optional[str]) -> Optional[datetime]:
    if not iso_str:
        return None
    # Python 3.11+: fromisoformat handles Z by replace
    if iso_str.endswith("Z"):
        iso_str = iso_str[:-1] + "+00:00"
    return datetime.fromisoformat(iso_str)

def _pick_base_component(bases: List):
    """Prefer component with RRULE; else earliest DTSTART."""
    with_rrule = [b for b in bases if b.get("RRULE")]
    if with_rrule:
        return with_rrule[0]
    return sorted(bases, key=lambda b: _decoded_dt(b, "DTSTART"))[0]
