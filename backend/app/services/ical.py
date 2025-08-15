from icalendar import Calendar

from app.utils.date import _ensure_aware, _parse_iso, decoded_dt_with_tz

from datetime import datetime, timedelta, timezone, date
from typing import Dict, List, Optional
import requests
import os

from app.models.models import (
    Event, RecurrenceRule, EventOccurrence,
    RecurrenceExdate, RecurrenceRdate, EventOverride, CalendarSource
)

from app.models.recurrence_rule import add_recurrence_rule
from app.models.event_occurrence import populate_event_occurrences, save_event_occurrence
from app.models.event import save_event

LOOKAHEAD_DAYS = 180  # window for generating occurrences

def import_ical_feed_using_helpers(
    db_session,
    ical_text_or_url: str,
    *,
    org_id: int,
    category_id: int,
    default_event_type: Optional[str] = None,   # e.g. "CLUB"/"ACADEMIC"/"CAREER"/"OH"/NONE
    source_url: Optional[str] = None,
    # user_edited: Optional[List[int]] = None,
    user_id: Optional[int] = None,
    delete_missing_uids: bool = False           # if True, remove events that disappeared from feed
):
    """
    Parse an ICS (string or URL), group by UID, and upsert events using the same logic
    as /create_event. All datetimes passed to helpers as ISO strings.
    """
    # 1) Load ICS (support webcal:// or https:// or raw text)
    ical_text = _fetch_ics_text(ical_text_or_url)

    cal = Calendar.from_ical(ical_text)

    event_ids = []

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
        event_id = _process_uid_group_with_helpers(
            db_session=db_session,
            uid=uid,
            components=components,
            now=now,
            horizon=horizon,
            org_id=org_id,
            category_id=category_id,
            default_event_type=default_event_type,
            source_url=source_url,
            user_id=user_id
        )
        if event_id:
            event_ids.append(event_id)

    # 4) Optionally delete events no longer present
    if delete_missing_uids:
        existing_uids = {row[0] for row in db_session.query(Event.ical_uid).filter(Event.org_id==org_id, Event.category_id==category_id).all()}
        missing = list(existing_uids - incoming_uids)
        if missing:
            db_session.query(Event).filter(Event.ical_uid.in_(missing)).delete(synchronize_session=False)

    return f"Processed {len(incoming_uids)} unique UIDs from ICS feed:\n{event_ids}"


## this function (sync_ical_source) has not been tested yet, do not run in production environment
# def sync_ical_source(db, source: CalendarSource):
#     # Acquire soft lock
#     if source.locked_at and (datetime.now(timezone.utc) - source.locked_at).total_seconds() < 1800:
#         return "locked"
#     source.locked_at = datetime.now(timezone.utc)
#     source.lock_owner = os.getenv("HOSTNAME", "worker")
#     db.flush()

#     try:
#         url = source.url.replace("webcal://", "https://")
#         headers = {}
#         if source.etag:
#             headers["If-None-Match"] = source.etag
#         if source.last_modified_hdr:
#             headers["If-Modified-Since"] = source.last_modified_hdr.strftime("%a, %d %b %Y %H:%M:%S GMT")

#         resp = requests.get(url, headers=headers, timeout=30)
#         if resp.status_code == 304:
#             source.last_sync_status = "not_modified"
#         else:
#             resp.raise_for_status()
#             body = resp.text

#             # Optional extra guard
#             h = hashlib.sha256(body.encode("utf-8")).hexdigest()
#             if h == source.content_hash and source.sync_mode == "delta":
#                 source.last_sync_status = "not_modified"
#             else:
#                 status = import_ical_feed_using_helpers(
#                     db_session=db,
#                     ical_text_or_url=body,   # pass raw ICS
#                     org_id=source.org_id,
#                     category_id=source.category_id,
#                     default_event_type=source.default_event_type,
#                 )
#                 source.content_hash = h
#                 source.last_sync_status = "ok"

#             source.etag = resp.headers.get("ETag") or source.etag
#             lm = resp.headers.get("Last-Modified")
#             if lm:
#                 source.last_modified_hdr = parsed_httpdate_to_dt(lm)

#         source.last_fetched_at = datetime.now(timezone.utc)
#         source.next_due_at = source.last_fetched_at + timedelta(seconds=source.fetch_interval_seconds)
#         db.flush()
#         return source.last_sync_status
#     except Exception as e:
#         source.last_error = str(e)[:500]
#         source.last_sync_status = "error"
#         db.flush()
#         raise
#     finally:
#         # Release lock
#         source.locked_at = None
#         source.lock_owner = None
#         db.flush()


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
    # user_edited: Optional[bool],
    user_id: Optional[int]
):
    # Split: base components (no RECURRENCE-ID) vs overrides
    base_candidates = [c for c in components if not c.get("RECURRENCE-ID")]
    override_components = [c for c in components if c.get("RECURRENCE-ID")]

    if not base_candidates:
        return

    base = _pick_base_component(base_candidates)

    # Base fields
    dtstart = decoded_dt_with_tz(base, "DTSTART")  # aware datetime or date
    dtend   = decoded_dt_with_tz(base, "DTEND")
    is_all_day = _is_all_day_component(base)

    # Convert to ISO strings for your helper
    start_iso = _to_iso_for_helper(dtstart, is_all_day)
    end_iso   = _to_iso_for_helper(dtend,   is_all_day) if dtend else start_iso

    title = str(base.get("SUMMARY") or "").strip()
    description = str(base.get("DESCRIPTION") or "").strip()
    location = str(base.get("LOCATION") or "no location recorded").strip()

    seq = int(base.get("SEQUENCE", 0) or 0)
    lm  = base.get("LAST-MODIFIED")
    last_modified = lm.dt if lm else None

    # --- DEDUPE LOOKUP (scope by org+category; add source_id if you have it) ---
    existing = (db_session.query(Event)
                .filter_by(org_id=org_id, category_id=category_id, ical_uid=uid)
                .first())
    
    changed = _should_update(existing, seq, last_modified)

    # Upsert the Event by UID (using your helper flow)
    # We mirror the /create_event argument structure and then set iCal metadata after flush.
    # existing = db_session.query(Event).filter_by(ical_uid=uid).first()

    if existing:
        # Decide if we should update (SEQUENCE or LAST-MODIFIED newer)
        if changed:
            
            existing.title = title
            existing.description = description or ""
            existing.location = location or "no location recorded"
            existing.start_datetime = _ensure_aware(dtstart)
            existing.end_datetime = _ensure_aware(dtend) if dtend else _ensure_aware(dtstart)
            existing.is_all_day = is_all_day
            existing.source_url = source_url
            existing.event_type = default_event_type


            user_edited = existing.user_edited if existing.user_edited else []
            user_edited.append(user_id)
            existing.user_edited = user_edited

            existing.org_id = org_id
            existing.category_id = category_id
            existing.ical_sequence = seq
            if last_modified:
                existing.ical_last_modified = _ensure_aware(last_modified)
            db_session.flush()
            event = existing
        else:
            print(f"No changes detected for event {existing.id}")
            # will skip the rest of the steps for this event.
            return existing.id
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
            user_edited=[user_id]
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
        by_day = rrule.get("BYDAY", [])
        if isinstance(by_day, str):
            by_day = [by_day]  # Wrap in list if single string

        recurrence_data = {
            "frequency": (rrule.get("FREQ") or [None])[0],
            "interval":  (rrule.get("INTERVAL") or [1])[0],
            "start_datetime": start_iso,
            "count":     (rrule.get("COUNT") or [None])[0],
            "until":     until_iso,
            "by_day":    by_day,
            "by_month_day": (rrule.get("BYMONTHDAY") or [None])[0],
            "by_month":     (rrule.get("BYMONTH") or [None])[0],
        }

        # Upsert rule using your helper
        existing_rule = db_session.query(RecurrenceRule).filter_by(event_id=event.id).first()
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
        db_session.query(RecurrenceExdate).filter_by(rrule_id=rule.id).delete(synchronize_session=False)
        db_session.query(RecurrenceRdate).filter_by(rrule_id=rule.id).delete(synchronize_session=False)

        for ex in base.get("EXDATE", []):
            for exdate in ex.dts:
                db_session.add(RecurrenceExdate(
                    rrule_id=rule.id,
                    exdate=_ensure_aware(exdate.dt)
                ))

        for r in base.get("RDATE", []):
            for rdate in r.dts:
                db_session.add(RecurrenceRdate(
                    rrule_id=rule.id,
                    rdate=_ensure_aware(rdate.dt)
                ))
        db_session.flush()

        # Store overrides for this UID (RECURRENCE-ID)
        db_session.query(EventOverride).filter_by(rrule_id=rule.id).delete(synchronize_session=False)
        for oc in override_components:
            rid = oc.get("RECURRENCE-ID")
            if not rid:
                continue
            db_session.add(EventOverride(
                rrule_id=rule.id,
                recurrence_date=_ensure_aware(rid.dt),
                new_start=decoded_dt_with_tz(oc, "DTSTART"),
                new_end=decoded_dt_with_tz(oc, "DTEND"),
                new_title=str(oc.get("SUMMARY") or None),
                new_description=str(oc.get("DESCRIPTION") or None),
                new_location=str(oc.get("LOCATION") or None),
            ))
        db_session.flush()

        # Regenerate occurrences
        # (populate_event_occurrences reads rule + exdates/rdates/overrides)
        populate_event_occurrences(db_session, event=event, rule=rule)

    else:
        # One-time event: clean any previous rule + just write one occurrence
        old_rule = db_session.query(RecurrenceRule).filter_by(event_id=event.id).first()
        if old_rule and changed:
            db_session.query(RecurrenceExdate).filter_by(rrule_id=old_rule.id).delete(synchronize_session=False)
            db_session.query(RecurrenceRdate).filter_by(rrule_id=old_rule.id).delete(synchronize_session=False)
            # since we set ON DELETE CASCADE for overrides linked to rule, this single delete is enough:
            db_session.delete(old_rule)
            db_session.flush()
        
        if changed or not _has_occurrence(db_session, event.id, _ensure_aware(dtstart), _ensure_aware(dtend) if dtend else _ensure_aware(dtstart)):

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
                user_edited=[user_id],
                description=description or None,
                location=location or None,
                source_url=source_url
            )
    return event.id

    # Optional: if you want occurrences only up to `horizon`, keep your populate logic bounded by a horizon.


# -----------------------
# Utilities
# -----------------------

def _has_occurrence(db_session, event_id: int, start_dt, end_dt) -> bool:
    q = (db_session.query(EventOccurrence.id)
         .filter_by(event_id=event_id)
         .filter(EventOccurrence.start_datetime == start_dt))
    if end_dt is not None:
        q = q.filter(EventOccurrence.end_datetime == end_dt)
    return db_session.query(q.exists()).scalar()

def _fetch_ics_text(ical_text_or_url: str) -> str:
    s = ical_text_or_url.strip()
    if s.startswith(("http://", "https://", "webcal://")):
        if s.startswith("webcal://"):
            s = "https://" + s[len("webcal://"):]
        r = requests.get(s, timeout=30)
        r.raise_for_status()
        return r.text
    return s  # already raw ICS text

def _should_update(existing_evt: Event, seq: int, last_modified: datetime) -> bool:
        if existing_evt is None:
            return True
        if seq > (existing_evt.ical_sequence or 0):
            return True
        if last_modified and (
            existing_evt.ical_last_modified is None
            or last_modified > existing_evt.ical_last_modified
        ):
            return True
        return False

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

def _pick_base_component(bases: List):
    """Prefer component with RRULE; else earliest DTSTART."""
    with_rrule = [b for b in bases if b.get("RRULE")]
    if with_rrule:
        return with_rrule[0]
    return sorted(bases, key=lambda b: decoded_dt_with_tz(b, "DTSTART"))[0]
