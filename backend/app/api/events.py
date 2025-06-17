from flask import Blueprint, jsonify, request
from app.models.user import get_user_by_clerk_id, create_user, user_to_dict
from app.services.google_service import fetch_user_credentials
from app.models.user import update_user_calendar_id
from app.services.google_service import create_cmucal_calendar
from app.services.db import SessionLocal
from app.models.event import create_event
from app.models.career import save_career
from app.models.academic import save_academic
from app.models.club import save_club


events_bp = Blueprint("events", __name__)

@events_bp.route("/create_event", methods=["POST"])
def create_event_record():
    db = SessionLocal()
    try:
        data = request.get_json()
        title = data.get("title")
        description = data.get("description", None)
        start_datetime = data.get("start_datetime")
        end_datetime = data.get("end_datetime")
        is_all_day = data.get("is_all_day", False)
        location = data.get("location", None)
        source_url = data.get("source_url", None)
        resource= data.get("resource", None)
        is_uploaded = data.get("is_uploaded", False)
        org_id = data.get("org_id")
        category_id = data.get("category_id")

        if not org_id or not category_id:
            db.rollback()
            return jsonify({"error": "Missing org_id or category_id"}), 400
        
        if not title or not start_datetime or not end_datetime:
            db.rollback()
            return jsonify({"error": "Missing required fields: title, start_datetime, end_datetime"}), 400
        

        # Assuming you have a function to create an event
        event = create_event(db, org_id=org_id, 
                             category_id=category_id,
                             title=title,
                             description=description,
                             start_datetime=start_datetime,
                             end_datetime=end_datetime,
                             is_all_day=is_all_day,
                             location=location,
                             source_url=source_url,
                             resource=resource,
                             is_uploaded=is_uploaded)
        
        if resource == "CAREER":
            career = save_career(db,
                        event_id=event.id, 
                        host=data.get("host", None),
                        link=data.get("link", None),
                        registration_required=data.get("registration_required", None))
        elif resource == "ACADEMIC":
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
        elif resource == "CLUB":
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

