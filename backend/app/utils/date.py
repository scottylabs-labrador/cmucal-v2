from datetime import date, datetime, timezone
from typing import Dict, List, Optional
from zoneinfo import ZoneInfo

DEFAULT_TZ = ZoneInfo("America/New_York")  # pick what’s right for your feed


def parse_user_datetime(date_str: str, time_str: str, tz_str: str = "UTC") -> datetime:
    """
    Converts user-submitted date and time strings into a timezone-aware datetime object.

    Args:
        date_str: Date string in 'YYYY-MM-DD' format (e.g., '2025-09-11')
        time_str: Time string in 'HH:MM' format (24-hour clock, e.g., '19:00')
        tz_str: IANA timezone string (e.g., 'America/New_York'). Defaults to 'UTC'.

    Returns:
        timezone-aware datetime object
    """
    dt_str = f"{date_str} {time_str}"
    try:
        naive = datetime.strptime(dt_str, "%Y-%m-%d %H:%M")
    except ValueError:
        raise ValueError(f"Invalid datetime string: {dt_str}")

    try:
        tz = ZoneInfo(tz_str)
    except Exception:
        raise ValueError(f"Invalid timezone: {tz_str}")
    
    aware_dt = naive.replace(tzinfo=tz)
    
    # if want iso string:
    return aware_dt.isoformat()

    # if want datetime object:
    # return aware_dt

# print(parse_user_datetime("2025-06-17", "13:37", "America/New_York"))

# def _decoded_dt(component, key: str):
#     """Return a timezone-aware datetime if present; if a DATE-only, convert to midnight UTC."""
#     if not component.get(key):
#         return None
#     val = component.decoded(key)
#     # val can be date or datetime
#     if isinstance(val, date) and not isinstance(val, datetime):
#         # All-day date → normalize to midnight UTC
#         return datetime(val.year, val.month, val.day, tzinfo=timezone.utc)
#     # Ensure tz-aware
#     return _ensure_aware(val)

def decoded_dt_with_tz(component, key: str, default_tz: ZoneInfo = DEFAULT_TZ):
    prop = component.get(key)
    if not prop:
        return None

    dt = component.decoded(key)  # may be date or datetime; may have tz

    # All-day DATE (no time)
    if isinstance(dt, date) and not isinstance(dt, datetime):
        # represent midnight in the default_tz; DB will store as UTC
        return datetime(dt.year, dt.month, dt.day, 0, 0, tzinfo=default_tz)

    # DATE-TIME
    if isinstance(dt, datetime):
        if dt.tzinfo is not None:
            return dt  # already aware (could be a VTIMEZONE tz)
        # Try TZID param on the property
        tzid = getattr(prop, "params", {}).get("TZID")
        tz = ZoneInfo(tzid) if tzid else default_tz
        return dt.replace(tzinfo=tz)

    return None


def _ensure_aware(dt):
    if dt is None:
        return None
    if isinstance(dt, date) and not isinstance(dt, datetime):
        dt = datetime(dt.year, dt.month, dt.day)
    if dt.tzinfo is None:
        return dt.replace(tzinfo=timezone.utc)
    return dt

def _parse_iso(iso_str: Optional[str]) -> Optional[datetime]:
    if not iso_str:
        return None
    # Python 3.11+: fromisoformat handles Z by replace
    if iso_str.endswith("Z"):
        iso_str = iso_str[:-1] + "+00:00"
    return datetime.fromisoformat(iso_str)

def _parse_iso_aware(s: str = None):
    if not s:
        return None
    # Support trailing 'Z'
    if isinstance(s, str) and s.endswith("Z"):
        s = s[:-1] + "+00:00"
    dt = datetime.fromisoformat(s) if isinstance(s, str) else s
    # Ensure tz-aware
    if dt.tzinfo is None:
        dt = dt.replace(tzinfo=timezone.utc)
    return dt

def convert_to_iso8601(dt_str):
    return datetime.strptime(dt_str, "%a, %d %b %Y %H:%M:%S %Z").isoformat() + "Z"