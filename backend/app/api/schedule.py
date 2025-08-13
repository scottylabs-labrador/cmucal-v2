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
        "recurrence": occurrence.recurrence.name if occurrence.recurrence else None,
        "event_id": occurrence.event_id,
        "org_id": occurrence.org_id,
        "category_id": occurrence.category_id,
    }

@schedule_bp.route('/', methods=['GET'])
def get_schedule_route():
    clerk_user_id = request.headers.get('Clerk-User-Id')
    schedule_id = request.args.get('schedule_id')
    user = get_current_user(clerk_user_id)

    if not user:
        return jsonify({"error": "User not found"}), 404

    with SessionLocal() as db:
        try:
            # Get specific schedule or user's first schedule
            schedule_query = db.query(Schedule).filter(Schedule.user_id == user.id)
            if schedule_id:
                schedule = schedule_query.filter(Schedule.id == schedule_id).first()
            else:
                schedule = schedule_query.first()

            if not schedule:
                return jsonify({"courses": [], "clubs": []})

            courses = {}
            clubs = {}

            # Get all organizations in the schedule
            for schedule_org in schedule.schedule_orgs:
                org = schedule_org.org
                if not org:
                    continue

                # Get all categories for this org
                categories = db.query(Category).filter(Category.org_id == org.id).all()
                
                # Get all events and occurrences for this org
                events_query = db.query(Event).filter(Event.org_id == org.id)
                
                # Check if org is a course or club
                if org.type == "COURSE" or org.type == "ACADEMIC":
                    courses[org.id] = {
                        "org_id": org.id,
                        "name": org.name,
                        "categories": [],
                        "events": {}
                    }
                    
                    # Add categories and their events
                    for category in categories:
                        courses[org.id]["categories"].append({
                            "id": category.id,
                            "name": category.name
                        })
                        
                        # Get events for this category
                        events = db.query(Event).filter(
                            Event.org_id == org.id,
                            Event.category_id == category.id
                        ).all()
                        
                        # Get event occurrences
                        event_ids = [e.id for e in events]
                        occurrences = db.query(EventOccurrence).filter(
                            EventOccurrence.event_id.in_(event_ids)
                        ).all()
                        
                        courses[org.id]["events"][category.name] = [event_occurrence_to_dict(o) for o in occurrences]
                
                elif org.type == "CLUB":
                    clubs[org.id] = {
                        "org_id": org.id,
                        "name": org.name,
                        "categories": [],
                        "events": {}
                    }
                    
                    # Add categories and their events
                    for category in categories:
                        clubs[org.id]["categories"].append({
                            "id": category.id,
                            "name": category.name
                        })
                        
                        # Get regular events for this category
                        events = db.query(Event).filter(
                            Event.org_id == org.id,
                            Event.category_id == category.id
                        ).all()

                        # Convert regular events to the same format as occurrences
                        event_list = [{
                            "id": event.id,
                            "title": event.title,
                            "description": event.description,
                            "start_datetime": event.start_datetime.isoformat(),
                            "end_datetime": event.end_datetime.isoformat(),
                            "location": event.location,
                            "is_all_day": event.is_all_day,
                            "source_url": event.source_url,
                            "recurrence": None,
                            "event_id": event.id,
                            "org_id": event.org_id,
                            "category_id": event.category_id,
                        } for event in events]
                        
                        # Get event occurrences if any exist
                        event_ids = [e.id for e in events]
                        if event_ids:
                            occurrences = db.query(EventOccurrence).filter(
                                EventOccurrence.event_id.in_(event_ids)
                            ).all()
                            event_list.extend([event_occurrence_to_dict(o) for o in occurrences])
                        
                        clubs[org.id]["events"][category.name] = event_list

            return jsonify({"courses": list(courses.values()), "clubs": list(clubs.values())})
        except Exception as e:
            db.rollback()
            import traceback
            print("❌ Exception:", traceback.format_exc())
            return jsonify({"error": str(e)}), 500

@schedule_bp.route('/category/<int:category_id>', methods=['DELETE'])
def remove_category_from_schedule(category_id):
    clerk_user_id = request.headers.get('Clerk-User-Id')
    user = get_current_user(clerk_user_id)

    if not user:
        return jsonify({"error": "User not found"}), 404
    
    with SessionLocal() as db:
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