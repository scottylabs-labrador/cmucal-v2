import json
from datetime import datetime

from app.scraper.models_scraper import RecurrenceRule, CareerMeta, AcademicMeta


def test_recurrence_defaults():
    start = datetime(2025, 1, 1, 9, 0)
    rr = RecurrenceRule(start_datetime=start,
                        frequency="DAILY",
                        interval=1)

    data = rr.to_json()

    # minimal fields
    assert data["frequency"] == "DAILY"
    assert data["interval"] == 1
    # datetime turned into ISO-8601 string
    assert data["start_datetime"] == "2025-01-01T09:00:00"
    # optional fields default to None
    for key in ("count", "until", "by_day", "by_month_day", "by_month"):
        assert data[key] is None

    # round-trip check: JSON serialization should not raise
    json.dumps(data)   # will raise TypeError if any value is not JSON-serializable


def test_recurrence_full():
    start = datetime(2025, 6, 27, 15, 30)
    until = datetime(2025, 12, 31)
    rr = RecurrenceRule(start, "WEEKLY", 2,
                        count=10,
                        until=until,
                        by_day=["MO", "WE", "FR"],
                        by_month_day=[15, 30],
                        by_month=[1, 7])

    d = rr.to_json()
    assert d["until"] == "2025-12-31T00:00:00"
    assert d["by_day"] == ["MO", "WE", "FR"]
    assert d["by_month_day"] == [15, 30]
    assert d["by_month"] == [1, 7]


def test_career_meta_to_json():
    cm = CareerMeta(1, "CMU Career Center",
                    "https://careers.cmu.edu/event/123",
                    True)

    assert cm.to_json() == {
        "event_id" : 1,
        "host": "CMU Career Center",
        "link": "https://careers.cmu.edu/event/123",
        "registration_required": True,
    }
