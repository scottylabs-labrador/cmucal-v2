from flask import Blueprint, request, jsonify
# from app.services.db import get_db
# import os
# from app.config.settings import Config
from app.services.db import Base, SessionLocal
from sqlalchemy import text
from app.models.models import User 


base_bp = Blueprint("base", __name__)

@base_bp.route("/")
def home():
    print('hi')
    print('there')
    return "Welcome to the CMUCal Flask API!"


@base_bp.route("/test_db", methods=["GET"])
def db_health_check():
    with SessionLocal() as db:
        try:
            user = User(clerk_id="123456")
            db.add(user)
            db.commit()
            db.refresh(user)
            return jsonify({"status": "connected"})
        except Exception as e:
            return jsonify({"status": "error", "details": str(e)}), 500
        
@base_bp.route("/test_rrule", methods=["GET"])
def test_rrule():
    from app.models.recurrence_rule import get_rrule_from_db_rule
    from app.models.models import RecurrenceRule
    from app.models.enums import FrequencyType
    from datetime import datetime, timedelta, timezone
    from dateutil.rrule import (
        rrule,
        DAILY, WEEKLY, MONTHLY, YEARLY,
        MO, TU, WE, TH, FR, SA, SU,
        weekday,
    )

    with SessionLocal() as db:
        try:
            # rule = rrule(
            #     freq=MONTHLY,
            #     dtstart=datetime(2025, 7, 25),
            #     byweekday=FR(-1),
            #     count=5
            # )

            # for dt in rule:
            #     print(dt.date())

            # rule = RecurrenceRule(
            #     frequency="MONTHLY",                # or Enum(Frequency.MONTHLY)
            #     interval=1,
            #     start_datetime=datetime(2025, 7, 1, 13, 0, tzinfo=timezone.utc),  # 1pm UTC
            #     count=5,
            #     until=None,
            #     by_day=["-1FR"],                    # last Friday of month
            #     by_month_day=None,                 # must be None to avoid override
            #     by_month=None                      # all months
            # )

            # rrule = get_rrule_from_db_rule(rule)


            

            start = datetime.now(timezone.utc) - timedelta(days=1)
            until = datetime.now(timezone.utc) + timedelta(days=5)

            rule = rrule(freq=DAILY, dtstart=start, until=until)

            print(list(rule))  # ✅ prints 6 daily dates

            # for dt in rrule:
            #     print(dt.date())

            return jsonify({"rrule": str(rrule)})
        except Exception as e:
            return jsonify({"error": str(e)}), 500
