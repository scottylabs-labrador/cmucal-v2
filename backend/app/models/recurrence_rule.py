from app.models.models import RecurrenceRule
from app.models.enums import FrequencyType
from datetime import datetime, timedelta, timezone
from dateutil.rrule import (
    rrule,
    DAILY, WEEKLY, MONTHLY, YEARLY,
    MO, TU, WE, TH, FR, SA, SU,
    weekday,
)
from typing import List, Optional, Union
from dateutil.parser import parse as parse_datetime
from app.utils.date import _ensure_aware

def add_recurrence_rule(db, event_id: int, frequency: FrequencyType,  
                        interval: int, start_datetime: str, count: int = None, until: str = None, 
                        by_month: int = None, by_month_day: int = None, by_day: List[str] = None):
    """
    Adds a recurrence rule to the database. If count is set, it will respect the count.
    If count is not set and until is set, it will respect the until date with a 6-month cap, and add orig_until to the database.
    If both count and until are not set, it will use a 6-month cap from now, and add orig_until to the database.

    when rendering the rule, it will use the count or until date to determine the end of the recurrence (regenerate if count is NULL).
    """
    six_months_later = datetime.now(timezone.utc) + timedelta(days=180)
    orig_until = None

    if isinstance(until, str):
        until = parse_datetime(until)

    if count is None:
        orig_until = until
        if until is None:
            until = six_months_later
        else:
            until = min(until, six_months_later)

    new_rule = RecurrenceRule(
        frequency=frequency,
        interval=interval,
        start_datetime=start_datetime,
        count=count,
        until=until,
        event_id=event_id,  
        by_month=by_month,
        by_month_day=by_month_day,
        by_day=by_day,
        orig_until=orig_until  # Store the original until date if applicable
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

FREQ_MAP = {
    "DAILY": DAILY,
    "WEEKLY": WEEKLY,
    "MONTHLY": MONTHLY,
    "YEARLY": YEARLY,
}


def parse_by_day_array(by_day_list: Optional[List[str]]) -> Optional[List[Union[weekday]]]:
    """
    Converts a list like ["MO", "3FR", "-1TU"] into dateutil.rrule weekday objects.
    """
    if not by_day_list:
        return None

    byweekday = []
    for item in by_day_list:
        if not item:
            continue
        item = item.strip().upper()

        if len(item) > 2 and item[:-2].lstrip("-").isdigit():
            pos = int(item[:-2])
            day = item[-2:]
            if day in WEEKDAY_MAP:
                day_const = WEEKDAY_MAP[day]
                byweekday.append(weekday(day_const.weekday, pos)) 
            else:
                print(f"Skipping unrecognized day: {item}")
        elif item in WEEKDAY_MAP:
            byweekday.append(WEEKDAY_MAP[item])
        else:
            print(f"Skipping unrecognized by_day entry: {item}")

    return byweekday if byweekday else None


def get_rrule_from_db_rule(rule) -> rrule:
    """
    Constructs a dateutil.rrule object from a database recurrence rule.
    Assumes `rule` has attributes: frequency, interval, start_datetime, count, until,
    by_day (List[str]), by_month (int or List[int]), by_month_day (int or List[int]).
    """
    freq_map = {
        'DAILY': DAILY,
        'WEEKLY': WEEKLY,
        'MONTHLY': MONTHLY,
        'YEARLY': YEARLY
    }

    # Fix: allow either Enum or string
    raw_freq = rule.frequency.value if hasattr(rule.frequency, "value") else rule.frequency
    freq = freq_map[raw_freq]
    if freq is None:
        raise ValueError(f"Unsupported frequency: {rule.frequency.value}")

    interval = rule.interval or 1
    start_datetime = rule.start_datetime
    count = rule.count
    until = rule.until

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

