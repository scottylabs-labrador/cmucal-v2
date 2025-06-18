from flask import Blueprint, jsonify, request
from app.models.user import get_user_by_clerk_id, create_user, user_to_dict
from app.services.google_service import fetch_user_credentials
from app.models.user import update_user_calendar_id
from app.services.google_service import create_cmucal_calendar
from app.services.db import SessionLocal
from app.models.event import save_event
from app.models.career import save_career
from app.models.academic import save_academic
from app.models.club import save_club
from app.models.tag import get_tag_by_name, save_tag
from app.models.event_tag import save_event_tag
from app.models.recurrence_rule import add_recurrence_rule
from app.models.event_occurrence import populate_event_occurrences, save_event_occurrence
from app.models.models import Event
import pprint
from datetime import datetime


events_bp = Blueprint("events", __name__)

@events_bp.route("/create_event", methods=["POST"])
def create_event_record():
    db = SessionLocal()
    try:
        data = request.get_json()
        pprint.pprint(data)

        if not request.is_json:
            return jsonify({"error": "Invalid JSON body"}), 400
        title = data.get("title")
        description = data.get("description", None)
        start_datetime = data.get("start_datetime")
        end_datetime = data.get("end_datetime")
        is_all_day = data.get("is_all_day", False)
        location = data.get("location", None)
        source_url = data.get("source_url", None)
        event_type= data.get("event_type", None)
        is_uploaded = data.get("is_uploaded", False)
        org_id = data.get("org_id")
        category_id = data.get("category_id")
        event_tags = data.get("event_tags", None)

        if not org_id or not category_id:
            db.rollback()
            return jsonify({"error": "Missing org_id or category_id"}), 400
        
        if not title or not start_datetime or not end_datetime:
            db.rollback()
            return jsonify({"error": "Missing required fields: title, start_datetime, end_datetime"}), 400

        # Assuming you have a function to create an event
        event = save_event(db, org_id=org_id, 
                             category_id=category_id,
                             title=title,
                             description=description,
                             start_datetime=start_datetime,
                             end_datetime=end_datetime,
                             is_all_day=is_all_day,
                             location=location,
                             source_url=source_url,
                             event_type=event_type,
                             is_uploaded=is_uploaded)
        
        if not event:
            db.rollback()
            return jsonify({"error": "Event creation failed"}), 500
        
        if event_tags:
            for tag_name in event_tags:
                tag_name = tag_name.strip().lower()  # Normalize tag name to lowercase
                # first check if tag exists, if not create it
                tag = get_tag_by_name(db, tag_name)
                if not tag:
                    tag = save_tag(db, name=tag_name)
                # add tag to event
                if tag:
                    save_event_tag(db, event_id=event.id, tag_id=tag.id)
                else:
                    db.rollback()
                    return jsonify({"error": f"Failed to save tag '{tag_name}'"}), 500
        
        if event_type == "CAREER":
            career = save_career(db,
                        event_id=event.id, 
                        host=data.get("host", None),
                        link=data.get("link", None),
                        registration_required=data.get("registration_required", None))
        elif event_type == "ACADEMIC":
            course_num=data.get("course_num", None)
            course_name=data.get("course_name", None)
            instructors=data.get("instructors", None)
            if not course_num or not course_name:
                db.rollback()
                return jsonify({"error": "Missing required fields for academic event"}), 400
            academic = save_academic(db,
                        event_id=event.id, 
                        course_num=data.get("course_num", None),
                        course_name=data.get("course_name", None),
                        instructors=data.get("instructors", None))
        elif event_type == "CLUB":
            club = save_club(db, event_id=event.id)
        
        db.commit()  # Only commit if all succeeded
        return jsonify({"status": "event created", "event_id": event.id}), 201
    except Exception as e:
        db.rollback()
        import traceback
        print("❌ Exception:", traceback.format_exc())

        return jsonify({"error": str(e)}), 500
    finally:
        db.close()

@events_bp.route("/create_recurrence_rules", methods=["POST"])
def create_recurrence_rules():
    db = SessionLocal()
    try:
        data = request.get_json()
        event_id = data.get("event_id")
        frequency = data.get("frequency")
        interval = data.get("interval")
        start_datetime = data.get("start_datetime")
        count = data.get("count", None)
        until = data.get("until", None)
        by_day = data.get("by_day", None)
        by_month_day = data.get("by_month_day", None)
        by_month = data.get("by_month", None)
        
        if not event_id or not start_datetime or not frequency or not interval:
            db.rollback()
            return jsonify({"error": "Missing event_id or start_datetime or frequency or interval"}), 400
        
        event = db.query(Event).filter(Event.id == event_id).first()
        rule = add_recurrence_rule(db, 
                                   event_id=event_id, 
                                   frequency=frequency,
                                   interval=interval,
                                   start_datetime = start_datetime,
                                   count=count,
                                   until=until,
                                   by_day=by_day,
                                   by_month_day=by_month_day,
                                   by_month=by_month)
        occurrence_msg = populate_event_occurrences(db, event=event, rule=rule)
        db.commit()  # Only commit if all succeeded
        return jsonify({"status": f"recurrence rules created. {occurrence_msg}"}), 201
    except Exception as e:
        db.rollback()
        import traceback
        print("❌ Exception:", traceback.format_exc())
        return jsonify({"error": str(e)}), 500
    finally:
        db.close()

@events_bp.route("/create_single_event_occurrence", methods=["POST"])
def create_single_event_occurrence():
    db = SessionLocal()
    try:
        data = request.get_json()
        event_id = data.get("event_id")
        org_id = data.get("org_id")
        category_id = data.get("category_id")
        title = data.get("title")
        start_datetime = data.get("start_datetime")
        end_datetime = data.get("end_datetime")
        recurrence = data.get("recurrence")
        is_all_day = data.get("is_all_day", False)
        is_uploaded = data.get("is_uploaded", False)
        description = data.get("description", None)
        location = data.get("location", None)
        source_url = data.get("source_url", None)
        resource = data.get("resource", None)

        if not event_id or not org_id or not category_id or not title or not start_datetime or not end_datetime or not recurrence:
            db.rollback()
            return jsonify({"error": "Missing required fields"}), 400
        
        event = db.query(Event).filter(Event.id == event_id).first()
        if not recurrence == "EXCEPTION":
            event_saved_at = event.last_updated_at
        else:
            event_saved_at = datetime.utcnow()
        if not event:
            db.rollback()
            return jsonify({"error": "Event not found"}), 404

        event_occurrence = save_event_occurrence(db, 
                                               event_id=event_id, 
                                               org_id=org_id, 
                                               category_id=category_id, 
                                               title=title,
                                               start_datetime=start_datetime,
                                               end_datetime=end_datetime,
                                               recurrence=recurrence,
                                               event_saved_at=event_saved_at,
                                               is_all_day=is_all_day,
                                               is_uploaded=is_uploaded,
                                               description=description,
                                               location=location,
                                               source_url=source_url,
                                               resource=resource)
        
        db.commit()  # Only commit if all succeeded
        return jsonify({"status": f"event occurrence {event_occurrence.id} created."}), 201
    except Exception as e:
        db.rollback()
        import traceback
        print("❌ Exception:", traceback.format_exc())
        return jsonify({"error": str(e)}), 500
    finally:
        db.close()
