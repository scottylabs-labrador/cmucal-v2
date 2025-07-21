from app.models.models import RecurrenceRule
from app.models.enums import FrequencyType
from datetime import date, datetime
from dateutil.rrule import (
    rrule,
    DAILY, WEEKLY, MONTHLY, YEARLY,
    MO, TU, WE, TH, FR, SA, SU,
    weekday,
)
from typing import List, Optional, Union
from dateutil.parser import parse

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

