from app.models.models import CalendarSource, CategoryIcal

def create_calendar_source(
    db_session,
    url: str,
    org_id: int,
    category_id: int,
    active: bool,
    default_event_type: str,
    created_by_user_id: int,
    **kwargs
):
    # Build the base record with explicit fields
    record_data = {
        "url": url,
        "org_id": org_id,
        "category_id": category_id,
        "active": active,
        "default_event_type": default_event_type,
        "created_by_user_id": created_by_user_id,
    }

    # Merge in any other fields passed
    record_data.update(kwargs)

    # Example SQLAlchemy create
    calendar_source = CalendarSource(**record_data)
    db_session.add(calendar_source)
    db_session.flush()

    return calendar_source
