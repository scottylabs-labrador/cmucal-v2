from app.models.models import CategoryIcal

def create_category_ical(db_session, category_id, calendar_source_id):
    """
    Create a new CategoryIcal instance.
    """
    category_ical = CategoryIcal(category_id=category_id, calendar_source_id=calendar_source_id)
    db_session.add(category_ical)
    db_session.flush()
    return category_ical
