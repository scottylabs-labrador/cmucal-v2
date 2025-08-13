from app.models.models import Event 

from icalendar import Calendar, Event as IcalEvent
from recurring_ical_events import recurring_ical_events
from datetime import datetime, timedelta, timezone
from typing import Dict, List, Optional
import requests
from app.models.models import Event, RecurrenceRule, EventOccurrence, RecurrenceRDate, RecurrenceExDate, EventOverride


def is_all_day(component: IcalEvent) -> bool:
    dtstart = component.get('DTSTART')
    return dtstart and isinstance(dtstart.dt, datetime) and dtstart.params.get('VALUE') == 'DATE'

def parse_ical_and_store(ical_text: str, db, org_id, category_id, event_type):
    cal = Calendar.from_ical(ical_text)
    
    for component in cal.walk():
        if component.name != "VEVENT":
            continue

        # -- 1. UID --
        uid = str(component.get('UID'))

        # -- 2. Create the base event --
        title = str(component.get('SUMMARY'))
        description = str(component.get('DESCRIPTION', ''))
        location = str(component.get('LOCATION', ''))
        dtstart = component.decoded('DTSTART')
        dtend = component.decoded('DTEND')

        event = save_event(db, org_id=org_id, 
                                category_id=category_id,
                                title=title,
                                description=description,
                                start_datetime=dtstart,
                                end_datetime=dtend,
                                is_all_day=is_all_day(component),
                                location=location,
                                event_type=event_type)
            
        if not event:
            print(f"Failed to create event for UID: {uid}")
            continue

        # -- 3. Detect override instance --
        recurrence_id = component.get('RECURRENCE-ID')
        if recurrence_id:
            # Find the recurrence rule this belongs to
            recurrence_datetime = recurrence_id.dt
            event_override = EventOverride(
                recurrence_date=recurrence_datetime,
                new_start=component.get('DTSTART').dt,
                new_end=component.get('DTEND').dt,
                new_title=str(component.get('SUMMARY')),
                new_description=str(component.get('DESCRIPTION')),
                new_location=str(component.get('LOCATION'))
            )
            db.add(event_override)
            db.flush()
            continue  # Skip normal VEVENT creation

        # -- 4. Store Recurrence Rule if present --
        rrule = component.get('RRULE')
        if rrule:
            rule = RecurrenceRule(
                event_id=event.id,
                frequency=rrule.get('FREQ', [None])[0],
                interval=rrule.get('INTERVAL', [1])[0],
                count=rrule.get('COUNT', [None])[0],
                until=rrule.get('UNTIL', [None])[0],
                by_day=','.join(rrule.get('BYDAY', [])),
                by_month_day=rrule.get('BYMONTHDAY', [None])[0],
                by_month=rrule.get('BYMONTH', [None])[0],
                start_datetime=dtstart
            )
            db.session.add(rule)
            db.session.flush()

            # -- 5. EXDATEs --
            for ex in component.get('EXDATE', []):
                for exdate in ex.dts:
                    db.session.add(RecurrenceExDate(
                        recurrence_id=rule.id,
                        exdate=exdate.dt
                    ))

            # -- 6. RDATEs --
            for r in component.get('RDATE', []):
                for rdate in r.dts:
                    db.session.add(RecurrenceRDate(
                        recurrence_id=rule.id,
                        rdate=rdate.dt
                    ))

            # -- 7. Generate occurrences --
            full_cal = Calendar()
            full_cal.add_component(component)  # ensure it's a valid calendar
            occurrences = recurring_ical_events.of(full_cal).between(
                datetime.now(), datetime.now().replace(year=datetime.now().year + 1)
            )

            for occ in occurrences:
                db.session.add(EventOccurrence(
                    event_id=event.id,
                    start_datetime=occ['DTSTART'].dt,
                    end_datetime=occ['DTEND'].dt,
                    title=occ.get('SUMMARY'),
                    description=occ.get('DESCRIPTION', ''),
                    location=occ.get('LOCATION', ''),
                    is_all_day=is_all_day(occ)
                ))

        else:
            # Non-recurring → store one occurrence
            db.session.add(EventOccurrence(
                event_id=event.id,
                start_datetime=dtstart,
                end_datetime=dtend,
                title=title,
                description=description,
                location=location,
                is_all_day=is_all_day(component)
            ))

    db.session.commit()


### need to check type of start_datetime, end_datetime before using them
def save_event(db, org_id: int, category_id: int, title: str, start_datetime: str, end_datetime: str, 
                 is_all_day: bool, user_edited: List[int], description: str = None, 
                 location: str = None, source_url: str = None, event_type: str = None):
    """
    Create a new event in the database.
    Args:
        db: Database session.
        org_id: ID of the organization.
        category_id: ID of the category.
        title: Title of the event.
        description: Description of the event (optional).
        start_datetime: Start datetime of the event.
        end_datetime: End datetime of the event.
        is_all_day: Whether the event is an all-day event.
        location: Location of the event (optional).
        source_url: Source URL for the event (optional).
        user_edited: A list of user IDs who has edited/uploaded the event.
    Returns:
        The created Event object.
    """
    event = Event(
        org_id=org_id,
        category_id=category_id,
        title=title,
        description=description,
        start_datetime=start_datetime,
        end_datetime=end_datetime,
        is_all_day=is_all_day,
        location=location,
        source_url=source_url,
        event_type=event_type,
        user_edited=user_edited
    )
    db.add(event)
    db.flush()      # Allocate event.id without committing
    db.refresh(event)
    return event

def get_event_by_id(db, event_id: int):
    """
    Retrieve an event by its ID.
    Args:
        db: Database session.
        event_id: ID of the event.
    Returns:
        The Event object if found, otherwise None.
    """
    return db.query(Event).filter(Event.id == event_id).first()
def delete_event(db, event_id: int):
    """
    Delete an event by its ID.
    Args:
        db: Database session.
        event_id: ID of the event to delete.
    Returns:
        True if the event was deleted, False if it was not found.
    """
    event = db.query(Event).filter(Event.id == event_id).first()
    if event:
        db.delete(event)
        db.commit()
        return True
    return False
def get_events_by_org(db, org_id: int):
    """
    Retrieve all events for a given organization.
    Args:
        db: Database session.
        org_id: ID of the organization.
    Returns:
        A list of Event objects.
    """
    return db.query(Event).filter(Event.org_id == org_id).all()