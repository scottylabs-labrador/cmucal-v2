from app.models.models import RecurrenceRule
from app.models.enums import FrequencyType
from typing import List
from datetime import date
from dateutil.rrule import rrule, MONTHLY, WEEKLY, DAILY, YEARLY, FR, MO, TU, WE, TH, SA, SU

def add_recurrence_rule(db, event_id: int, frequency: FrequencyType,  
                        interval: int, start_datetime: str, count: int = None, until: str = None, 
                        by_month: int = None, by_month_day: int = None, by_day: List[str] = None):
    new_rule = RecurrenceRule(
        frequency=frequency,
        interval=interval,
        start_datetime=start_datetime,
        count=count,
        until=until,
        event_id=event_id,  
        by_month=by_month,
        by_month_day=by_month_day,
        by_day=by_day
    )

    db.add(new_rule)
    db.flush()
    db.refresh(new_rule)
    return new_rule

# Mapping for weekday strings to dateutil constants
WEEKDAY_MAP = {
    'MO': MO,
    'TU': TU,
    'WE': WE,
    'TH': TH,
    'FR': FR,
    'SA': SA,
    'SU': SU
}

def parse_by_day_array(by_day_list):
    """
    Converts a list like ["MO", "3FR", "-1TU"] into rrule.byweekday objects.
    """
    byweekday = []
    for item in by_day_list:
        if item is None:
            continue
        item = item.strip().upper()

        if len(item) >= 3 and item[:-2].lstrip("-").isdigit():
            # Positional day, e.g. "3FR" or "-1TU"
            pos = int(item[:-2])
            day = item[-2:]
            if day in WEEKDAY_MAP:
                byweekday.append(WEEKDAY_MAP[day](pos))
        elif item in WEEKDAY_MAP:
            byweekday.append(WEEKDAY_MAP[item])
        else:
            print(f"Skipping unrecognized by_day entry: {item}")

    return byweekday if byweekday else None

def get_rrule_from_db_rule(rule):
    freq_map = {
        'DAILY': DAILY,
        'WEEKLY': WEEKLY,
        'MONTHLY': MONTHLY,
        'YEARLY': YEARLY
    }

    freq = freq_map[rule.frequency.value]
    interval = rule.interval or 1
    start_datetime = rule.start_datetime
    count = rule.count
    until = rule.until

    # Parse by_day
    by_day_array = parse_by_day_array(rule.by_day or [])

    by_month = rule.by_month
    by_month_day = rule.by_month_day


    kwargs = {
        "freq": freq,
        "dtstart": start_datetime,
        "interval": interval,
    }
    if count:
        kwargs["count"] = count
    if until:
        kwargs["until"] = until
    if by_day_array:
        kwargs["byweekday"] = by_day_array
    if by_month:
        kwargs["bymonth"] = [by_month] if isinstance(by_month, int) else by_month
    if by_month_day:
        kwargs["bymonthday"] = [by_month_day] if isinstance(by_month_day, int) else by_month_day

    return rrule(**kwargs)
