from flask import Blueprint, jsonify, request
from app.models.user import get_user_by_clerk_id, create_user, user_to_dict
from app.services.google_service import fetch_user_credentials
from app.models.user import update_user_calendar_id
from app.services.google_service import create_cmucal_calendar
from app.services.db import SessionLocal
from app.models.event import save_event, get_event_by_id
from app.models.career import save_career
from app.models.academic import save_academic
from app.models.admin import get_admin_by_org_and_user
from app.models.club import save_club
from app.models.tag import get_tag_by_name, save_tag, get_all_tags
from app.models.event_tag import save_event_tag, get_tags_by_event, delete_event_tag
from app.models.recurrence_rule import add_recurrence_rule
from app.models.event_occurrence import populate_event_occurrences, save_event_occurrence
from app.models.category import category_to_dict, get_category_by_id
from app.models.models import Event, UserSavedEvent, Organization, EventOccurrence, EventTag, Category, Tag
import pprint
from datetime import datetime
from sqlalchemy import cast, Date, or_


events_bp = Blueprint("events", __name__)

@events_bp.route("/create_event", methods=["POST"])
def create_event_record():
    with SessionLocal() as db:
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
            user_edited = data.get("user_edited", None)
            org_id = data.get("org_id")
            category_id = data.get("category_id")
            event_tags = data.get("event_tags", None)
            recurrence = data.get("recurrence", None)

            if not org_id or not category_id:
                db.rollback()
                return jsonify({"error": "Missing org_id or category_id"}), 400

            if not title or not start_datetime or not end_datetime or not recurrence:
                db.rollback()
                return jsonify({"error": "Missing required fields: title, start_datetime, end_datetime, recurrence"}), 400

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
                                user_edited=user_edited)
            
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
            
            if recurrence and recurrence != "ONETIME":
                recurrence_data = data.get("recurrence_data", {})
                if not recurrence_data:
                    db.rollback()
                    return jsonify({"error": "Missing recurrence data"}), 400
                rule = add_recurrence_rule(db,  
                                    event_id=event.id, 
                                    frequency=recurrence_data.get("frequency"),
                                    interval=recurrence_data.get("interval"),
                                    start_datetime=recurrence_data.get("start_datetime"),
                                    count=recurrence_data.get("count", None),
                                    until=recurrence_data.get("until", None),
                                    by_day=recurrence_data.get("by_day", None),
                                    by_month_day=recurrence_data.get("by_month_day", None),
                                    by_month=recurrence_data.get("by_month", None))
                occurrence_msg = populate_event_occurrences(db, event=event, rule=rule)
            else:
                if not recurrence == "EXCEPTION":
                    event_saved_at = event.last_updated_at
                else:
                    event_saved_at = datetime.utcnow()
                
                event_occurrence = save_event_occurrence(db, 
                                                    event_id=event.id, 
                                                    org_id=org_id, 
                                                    category_id=category_id, 
                                                    title=title,
                                                    start_datetime=start_datetime,
                                                    end_datetime=end_datetime,
                                                    recurrence=recurrence,
                                                    event_saved_at=event_saved_at,
                                                    is_all_day=is_all_day,
                                                    user_edited=user_edited,
                                                    description=description,
                                                    location=location,
                                                    source_url=source_url)
            db.commit()  # Only commit if all succeeded
            return jsonify({"status": "event created", "event_id": event.id}), 201
        except Exception as e:
            db.rollback()
            import traceback
            print("❌ Exception:", traceback.format_exc())

            return jsonify({"error": str(e)}), 500


# should only be used for testing purposes
@events_bp.route("/create_recurrence_rule", methods=["POST"])
def create_recurrence_rules():
    with SessionLocal() as db:
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

# should only be used for testing purposes
@events_bp.route("/create_single_event_occurrence", methods=["POST"])
def create_single_event_occurrence():
    with SessionLocal() as db:
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
            user_edited = data.get("user_edited", None)
            description = data.get("description", None)
            location = data.get("location", None)
            source_url = data.get("source_url", None)

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
                                                user_edited=user_edited,
                                                description=description,
                                                location=location,
                                                source_url=source_url)
            
            db.commit()  # Only commit if all succeeded
            return jsonify({"status": f"event occurrence {event_occurrence.id} created."}), 201
        except Exception as e:
            db.rollback()
            import traceback
            print("❌ Exception:", traceback.format_exc())
            return jsonify({"error": str(e)}), 500
        
@events_bp.route("/tags", methods=["GET"])
def get_tags():
    # print("🙇 geting tags 🙇")
    with SessionLocal() as db:
        try: 
            # print("here we go")
            tags = get_all_tags(db)
            # print("tags, ", tags)
            return jsonify([{"name": tag.name, "id": tag.id} for tag in tags]), 200
        except Exception as e:
            db.rollback()

            print("❌ Exception:", e)
            return jsonify({"error": str(e)}), 500

@events_bp.route("/<event_id>/tags", methods=["GET"])
def get_event_tags(event_id):
    with SessionLocal() as db:
        try:
            # # get user
            # clerk_id = request.args.get("user_id")
            # if not clerk_id:
            #     return jsonify({"error": "Missing user_id"}), 400
            # user = get_user_by_clerk_id(db, clerk_id)
            
            # # event = db.query(Event).filter_by(id=event_id).first()
            # event = get_event_by_id(db, event_id)
            # event_dict = event.as_dict()
            
            # org = db.query(Organization).filter_by(id=event.org_id).first()
            # event_dict["org"] = org.name
            # event_dict["user_is_admin"] = True if get_admin_by_org_and_user(db, event.org_id, user.id) else False

            # tags = (
            #     db.query(Tag.id, Tag.name)
            #     .join(Tag.event_tags) # relationship set up in models
            #     # .join(EventTag, Tag.id == EventTag.tag_id)  # explicit join condition
            #     .filter(EventTag.event_id == event_id)      # filter by the event id
            #     .all()
            # )
            tags = get_tags_by_event(db, event_id)

            tag_names = [{"id": t.id, "name": t.name} for t in tags]

            # # check if saved
            # if user:
            #     saved = db.query(UserSavedEvent.event_id).filter_by(user_id=user.id, event_id=event_id).first()
            #     event_dict["user_saved"] = (saved is not None)
            # else:
            #     event_dict["user_saved"] = False
            print("👉🏷🏷🏷🏷 👈 ", tag_names)

            return tag_names

        except Exception as e:
            db.rollback()
            import traceback
            print("❌ Exception:", traceback.format_exc())
            return jsonify({"error": str(e)}), 500

@events_bp.route("/", methods=["GET"])
def get_all_events():
    term = request.args.get("term").lower()
    tag_ids_raw = request.args.get("tags")
    tag_ids = tag_ids_raw.split(",") if tag_ids_raw else []
    date = request.args.get("date")
    # print("🔗🔗🔗😄 ", request.url)
    with SessionLocal() as db:
        try:
            # get user
            clerk_id = request.args.get("user_id")
            if not clerk_id:
                return jsonify({"error": "Missing user_id"}), 400
            user = get_user_by_clerk_id(db, clerk_id)

            # only select some columns to save loading cost
            events = db.query(Event.id, Event.title, Event.start_datetime, Event.end_datetime, 
                Event.location, Event.org_id, Event.category_id).join(Event.org)

            
            # if search term is applied, filter results
            if term:
                term_pattern = f"%{term}%"
                events = events.filter(or_(
                    Event.title.ilike(term_pattern),
                    Event.description.ilike(term_pattern),
                    Organization.name.ilike(term_pattern), 
                ))

            # if tags are applied, filter results
            if len(tag_ids) > 0:
                events = events.join(EventTag).filter(EventTag.tag_id.in_(tag_ids)).group_by(Event.id)

            # if date is applied, filter results
            if date:
                # events = events.filter(Event.start_datetime==date)
                events = events.filter(cast(Event.start_datetime, Date) == date)

            # check for saved events
            if user:
                added_ids = db.query(UserSavedEvent.event_id).filter_by(user_id=user.id).all()
                added_ids = set(row[0] for row in added_ids)
            else:
                added_ids = set()

            return [
                {
                    "id": e[0],
                    "title": e[1],
                    "start_datetime": e[2],
                    "end_datetime": e[3],
                    "location": e[4],
                    "org_id": e[5],
                    "category_id": e[6],
                    "user_saved": e[0] in added_ids
                }
                for e in events
            ]

        except Exception as e:
            db.rollback()
            import traceback
            print("❌ Exception:", traceback.format_exc())
            return jsonify({"error": str(e)}), 500

@events_bp.route("/<event_id>", methods=["GET"])
def get_specific_events(event_id):
    with SessionLocal() as db:
        try:
            # get user
            clerk_id = request.args.get("user_id")
            if not clerk_id:
                return jsonify({"error": "Missing user_id"}), 400
            user = get_user_by_clerk_id(db, clerk_id)
            
            # event = db.query(Event).filter_by(id=event_id).first()
            event = get_event_by_id(db, event_id)
            event_dict = event.as_dict()
            
            org = db.query(Organization).filter_by(id=event.org_id).first()
            event_dict["org"] = org.name
            event_dict["user_is_admin"] = True if get_admin_by_org_and_user(db, event.org_id, user.id) else False

            # check if saved
            if user:
                saved = db.query(UserSavedEvent.event_id).filter_by(user_id=user.id, event_id=event_id).first()
                event_dict["user_saved"] = (saved is not None)
            else:
                event_dict["user_saved"] = False

            return jsonify(event_dict)

        except Exception as e:
            db.rollback()
            import traceback
            print("❌ Exception:", traceback.format_exc())
            return jsonify({"error": str(e)}), 500

@events_bp.route("/<event_id>", methods=["PATCH"])
def update_event(event_id):
    print("🔗🔢", request.url)
    with SessionLocal() as db:
        try:
            data = request.get_json()
            print("🔢🔢🔢🔢🔢DATA ", data)
            
            event_data = data.get("updated_event", None)
            tag_data = data.get("updated_tags", None)
            recurrence_data = data.get("updated_recurrence", None)

            if not event_data: 
                return jsonify({"error": "No event data provided"}), 400

            # update the event itself
            event = db.query(Event).filter_by(id=event_id).first()
            if not event:
                return jsonify({"error": "Event not found"}), 400

            for key, value in event_data.items(): 
                if hasattr(event, key):
                    setattr(event, key, value)

            # update event tag
            if tag_data:
                # desired_tags = [t.strip().lower() for t in tag_data]
                desired_tags = [t["name"].strip().lower() for t in tag_data]
                current_tags = [t.name.strip().lower() for t in get_tags_by_event(db, event_id)]  # returns list of tag names
                # print("👑", desired_tags, "🥒", current_tags)
                for tag_name in desired_tags:
                    tag = get_tag_by_name(db, tag_name)
                    if not tag:
                        tag = save_tag(db, name=tag_name) # add new tag
                    if tag_name not in current_tags:
                        save_event_tag(db, event_id=event_id, tag_id=tag.id)

                # remove tags that are no longer in desired list
                for tag_name in current_tags:
                    if tag_name not in desired_tags:
                        tag = get_tag_by_name(db, tag_name)
                        delete_event_tag(db, event_id=event_id, tag_id=tag.id)


            # TODO: update the corresponding type table (academic/career/club)

            # TODO: update recurrence table

            db.commit()

            event_dict = event.as_dict()
            return jsonify(event_dict), 200


        except Exception as e:
            db.rollback()
            import traceback
            print("❌ Exception:", traceback.format_exc())
            return jsonify({"error": str(e)}), 500


@events_bp.route("user_saved_events", methods=["GET"])
def get_all_saved_events():
    with SessionLocal() as db:
        try:
            # get user
            print("🔗Request URL: ", request.url)
            clerk_id = request.args.get("user_id")
            # print("😮 [clerk_id] ", clerk_id)
            if not clerk_id:
                return jsonify({"error": "Missing user_id"}), 400
            user = get_user_by_clerk_id(db, clerk_id)
            # print("😀 [user] ", user)

            # only columns required for calendar view
            events = db.query(Event.id, Event.title, Event.start_datetime, Event.end_datetime)\
                .join(UserSavedEvent).filter(
                    UserSavedEvent.user_id == user.id
                ).all()

            return jsonify([e[0] for e in events]) 
            # [
            #     {
            #         "id": e[0],
            #         # "title": e[1],
            #         # "start": e[2].isoformat(),
            #         # "end": e[3].isoformat(),
            #     }
            #     for e in events
            # ]

        except Exception as e:
            db.rollback()
            import traceback
            print("❌ Exception:", traceback.format_exc())
            return jsonify({"error": str(e)}), 500

@events_bp.route("user_saved_event_occurrences", methods=["GET"])
def get_all_saved_events_occurrences():
    with SessionLocal() as db:
        try:
            # get user
            clerk_id = request.args.get("user_id")
            if not clerk_id:
                return jsonify({"error": "Missing user_id"}), 400
            user = get_user_by_clerk_id(db, clerk_id)

            event_occurrences = (db.query(EventOccurrence.id, EventOccurrence.title, 
            EventOccurrence.start_datetime, EventOccurrence.end_datetime, Event.id)
                .join(Event, EventOccurrence.event_id == Event.id)
                .join(UserSavedEvent, UserSavedEvent.event_id == Event.id)
                .filter(
                    UserSavedEvent.user_id == user.id
                ).all())

            return [
                {
                    "id": e[0],
                    "title": e[1],
                    "start": e[2].isoformat(),
                    "end": e[3].isoformat(),
                    "event_id": e[4]
                }
                for e in event_occurrences
            ]

        except Exception as e:
            db.rollback()
            import traceback
            print("❌ Exception:", traceback.format_exc())
            return jsonify({"error": str(e)}), 500

@events_bp.route("/user_saved_events", methods=["POST"])
def user_save_event():
    with SessionLocal() as db:
        try:
            data = request.get_json()
            # get user
            clerk_id = data.get("user_id")
            if not clerk_id:
                return jsonify({"error": "Missing user_id"}), 400
            user = get_user_by_clerk_id(db, clerk_id)

            new_entry = UserSavedEvent(
                user_id = user.id,
                event_id = data["event_id"],
                google_event_id = data["google_event_id"],
                saved_at = datetime.utcnow(),
            )
            db.add(new_entry)
            db.commit()
            return jsonify({"message": "Event added to user's saved events."}), 200
            
        except Exception as e:
            db.rollback()
            import traceback
            print("❌ Exception:", traceback.format_exc())
            return jsonify({"error": str(e)}), 500

@events_bp.route("/user_saved_events/<event_id>", methods=["DELETE"])
def user_unsave_event(event_id):
    with SessionLocal() as db:
        try:
            data = request.get_json()
            # get user
            clerk_id = data.get("user_id")
            if not clerk_id:
                return jsonify({"error": "Missing user_id"}), 400
            user = get_user_by_clerk_id(db, clerk_id)

            user_id = user.id
            entry = db.query(UserSavedEvent).filter_by(user_id=user_id, event_id=event_id).first()

            if entry:
                db.delete(entry)
                db.commit()
            return jsonify({"message": "Event removed from user's saved events."}), 200 
                
        except Exception as e:
            db.rollback()
            import traceback
            print("❌ Exception:", traceback.format_exc())
            return jsonify({"error": str(e)}), 500

@events_bp.route("/<category_id>/category", methods=["GET"])
def get_event_category(category_id):
    print("👀👀👀 ", request.url)
    with SessionLocal() as db:
        try:
            category = get_category_by_id(db, category_id)
            print("-------------------\n", jsonify(category_to_dict(category)), "-------------------\n")
            return jsonify(category_to_dict(category))
        
        except Exception as e:
            db.rollback()
            import traceback
            print("❌ Exception:", traceback.format_exc())
            return jsonify({"error": str(e)}), 500
