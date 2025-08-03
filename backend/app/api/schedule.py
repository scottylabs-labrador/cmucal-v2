from flask import Blueprint, jsonify, request
from app.services.db import SessionLocal
from app.models.models import User, Schedule, ScheduleOrg, Organization, Category, Event, UserSavedEvent
from app.models.user import get_user_by_clerk_id
from sqlalchemy.orm import joinedload

schedule_bp = Blueprint("schedule", __name__)

@schedule_bp.route("/", methods=["GET"])
def get_user_schedule():
    with SessionLocal() as db:
        try:
            clerk_id = request.args.get("user_id")
            if not clerk_id:
                return jsonify({"error": "Missing user_id"}), 400
            
            user = get_user_by_clerk_id(db, clerk_id)
            if not user:
                return jsonify({"error": "User not found"}), 404

            # Get user's schedule
            schedule = db.query(Schedule).filter(Schedule.user_id == user.id).first()
            if not schedule:
                return jsonify({"error": "Schedule not found"}), 404

            # Get organizations in the schedule with their categories
            orgs_with_data = db.query(Organization).join(
                ScheduleOrg, ScheduleOrg.org_id == Organization.id
            ).filter(
                ScheduleOrg.schedule_id == schedule.id
            ).options(
                joinedload(Organization.categories)
            ).all()

            # Get saved events for calendar display
            saved_events = db.query(Event).join(
                UserSavedEvent, UserSavedEvent.event_id == Event.id
            ).filter(
                UserSavedEvent.user_id == user.id
            ).all()

            # Format the response
            result = {
                "courses": [],
                "clubs": [],
                "saved_events": []
            }

            # Get all events for these organizations
            org_ids = [org.id for org in orgs_with_data]
            events = db.query(Event).filter(Event.org_id.in_(org_ids)).all()

            for org in orgs_with_data:
                org_data = {
                    "org_id": org.id,
                    "name": org.name,
                    "categories": []
                }

                for category in org.categories:
                    # Filter events that match both org_id and category_id
                    category_events = [
                        event for event in events
                        if event.org_id == org.id and event.category_id == category.id
                    ]
                    
                    category_data = {
                        "id": category.id,
                        "name": category.name,
                        "events": [{
                            "id": event.id,
                            "title": event.title,
                            "start_datetime": event.start_datetime.isoformat() if event.start_datetime else None,
                            "end_datetime": event.end_datetime.isoformat() if event.end_datetime else None,
                            "location": event.location,
                            "is_saved": any(se.id == event.id for se in saved_events)
                        } for event in category_events]
                    }
                    org_data["categories"].append(category_data)

                # Determine if it's a course or club based on org name/type
                if any(keyword in org.name.lower() for keyword in ["course", "class", "lecture"]):
                    result["courses"].append(org_data)
                else:
                    result["clubs"].append(org_data)

            # Add saved events for calendar
            result["saved_events"] = [{
                "id": event.id,
                "title": event.title,
                "start": event.start_datetime.isoformat() if event.start_datetime else None,
                "end": event.end_datetime.isoformat() if event.end_datetime else None,
                "location": event.location
            } for event in saved_events]

            return jsonify(result)

        except Exception as e:
            db.rollback()
            import traceback
            print("❌ Exception:", traceback.format_exc())
            return jsonify({"error": str(e)}), 500

@schedule_bp.route('/category/<int:category_id>', methods=['DELETE'])
def remove_category_from_schedule(category_id):
    clerk_user_id = request.headers.get('Clerk-User-Id')
    user = get_user_by_clerk_id(SessionLocal(), clerk_user_id)

    if not user:
        return jsonify({"error": "User not found"}), 404
    
    with SessionLocal() as db:
        try:
            schedule = db.query(Schedule).filter(Schedule.user_id == user.id).first()
            if not schedule:
                return jsonify({"error": "Schedule not found"}), 404

            schedule_category_to_delete = db.query(ScheduleOrg).filter(
                ScheduleOrg.schedule_id == schedule.id,
                ScheduleOrg.org_id == category_id
            ).first()

            if not schedule_category_to_delete:
                return jsonify({"error": "Category not found in schedule"}), 404

            db.delete(schedule_category_to_delete)
            db.commit()
            return jsonify({"message": "Category removed successfully"}), 200
        except Exception as e:
            db.rollback()
            return jsonify({"error": str(e)}), 500