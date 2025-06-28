from flask import Blueprint, jsonify, request
from sqlalchemy.orm import joinedload, subqueryload
from app.services.db import SessionLocal
from app.models.models import User, Schedule, ScheduleCategory, Category, Organization, EventOccurrence, Academic, Event
from app.utils.auth import get_current_user

schedule_bp = Blueprint('schedule_bp', __name__)

def event_occurrence_to_dict(occurrence: EventOccurrence):
    """Manually serialize EventOccurrence SQLAlchemy object to a dictionary."""
    return {
        "id": occurrence.id,
        "title": occurrence.title,
        "description": occurrence.description,
        "start_datetime": occurrence.start_datetime.isoformat(),
        "end_datetime": occurrence.end_datetime.isoformat(),
        "location": occurrence.location,
        "is_all_day": occurrence.is_all_day,
        "source_url": occurrence.source_url,
        "recurrence": occurrence.recurrence,
        "event_id": occurrence.event_id,
        "org_id": occurrence.org_id,
        "category_id": occurrence.category_id,
    }

@schedule_bp.route('/', methods=['GET'])
def get_schedule_route():
    clerk_user_id = request.headers.get('Clerk-User-Id')
    user = get_current_user(clerk_user_id)

    if not user:
        return jsonify({"error": "User not found"}), 404

    db = SessionLocal()
    try:
        user_schedule_info = db.query(User).filter(User.id == user.id).options(
            subqueryload(User.schedules).subqueryload(Schedule.schedule_categories).subqueryload(ScheduleCategory.category).joinedload(Category.org).options(
                subqueryload(Organization.events)
            )
        ).first()

        if not user_schedule_info or not user_schedule_info.schedules:
            return jsonify({"courses": [], "clubs": []})

        primary_schedule = user_schedule_info.schedules[0]
        subscribed_categories = [sc.category for sc in primary_schedule.schedule_categories]

        courses = {}
        clubs = {}
        sasc_org = db.query(Organization).filter(Organization.name == "SASC").first()

        for category in subscribed_categories:
            org = category.org
            academic_event_ids = [e.id for e in org.events]
            is_academic = db.query(Academic).filter(Academic.event_id.in_(academic_event_ids)).first() is not None

            if is_academic:
                if org.id not in courses:
                    academic_event = next((e for e in org.events if db.query(Academic).filter(Academic.event_id == e.id).first()), None)
                    if not academic_event: continue
                    
                    course_details = db.query(Academic).filter(Academic.event_id == academic_event.id).first()
                    courses[org.id] = {
                        "org_id": org.id,
                        "course_num": course_details.course_num,
                        "course_name": course_details.course_name,
                        "instructors": course_details.instructors,
                        "categories": [],
                        "events": {}
                    }
                
                courses[org.id]["categories"].append({"id": category.id, "name": category.name})
                event_occurrences = db.query(EventOccurrence).filter(EventOccurrence.category_id == category.id).all()
                courses[org.id]["events"][category.name.lower().replace(" ", "_")] = [event_occurrence_to_dict(e) for e in event_occurrences]

                if sasc_org:
                    related_sasc_events = db.query(Event).join(Academic).filter(
                        Event.org_id == sasc_org.id,
                        Academic.course_num == courses[org.id]["course_num"]
                    ).all()
                    if related_sasc_events:
                        sasc_event_ids = [e.id for e in related_sasc_events]
                        sasc_occurrences = db.query(EventOccurrence).filter(EventOccurrence.event_id.in_(sasc_event_ids)).all()
                        if sasc_occurrences:
                            if "sasc_events" not in courses[org.id]["events"]:
                                courses[org.id]["events"]["sasc_events"] = []
                            courses[org.id]["events"]["sasc_events"].extend([event_occurrence_to_dict(o) for o in sasc_occurrences])
            else:
                if org.id not in clubs:
                    clubs[org.id] = {
                        "org_id": org.id,
                        "name": org.name,
                        "description": org.description,
                        "categories": [],
                        "events": {}
                    }
                
                clubs[org.id]["categories"].append({"id": category.id, "name": category.name})
                event_occurrences = db.query(EventOccurrence).filter(EventOccurrence.category_id == category.id).all()
                clubs[org.id]["events"][category.name.lower().replace(" ", "_")] = [event_occurrence_to_dict(e) for e in event_occurrences]

        return jsonify({"courses": list(courses.values()), "clubs": list(clubs.values())})
    finally:
        db.close()

@schedule_bp.route('/category/<int:category_id>', methods=['DELETE'])
def remove_category_from_schedule(category_id):
    clerk_user_id = request.headers.get('Clerk-User-Id')
    user = get_current_user(clerk_user_id)

    if not user:
        return jsonify({"error": "User not found"}), 404
    
    db = SessionLocal()
    try:
        schedule = db.query(Schedule).filter(Schedule.user_id == user.id).first()
        if not schedule:
            return jsonify({"error": "Schedule not found"}), 404

        schedule_category_to_delete = db.query(ScheduleCategory).filter(
            ScheduleCategory.schedule_id == schedule.id,
            ScheduleCategory.category_id == category_id
        ).first()

        if not schedule_category_to_delete:
            return jsonify({"error": "Category not found in schedule"}), 404

        db.delete(schedule_category_to_delete)
        db.commit()
        return jsonify({"message": "Category removed successfully"}), 200
    except Exception as e:
        db.rollback()
        return jsonify({"error": str(e)}), 500
    finally:
        db.close() 