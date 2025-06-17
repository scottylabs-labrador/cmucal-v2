from datetime import datetime
try:
    from zoneinfo import ZoneInfo  # Python 3.9+
except ImportError:
    from tzlocal import get_localzone  # For older versions

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
    # return aware_dt.isoformat()

    return aware_dt

# print(parse_user_datetime("2025-06-17", "13:37", "America/New_York"))
