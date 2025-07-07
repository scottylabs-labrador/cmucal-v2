from flask import Blueprint, jsonify, request
from app.models.user import get_user_by_clerk_id, create_user, user_to_dict
from app.services.google_service import fetch_user_credentials
from app.models.user import update_user_calendar_id
from app.services.google_service import create_cmucal_calendar
from app.services.db import SessionLocal
from app.models.organization import create_organization
from app.models.admin import create_admin, get_categories_for_admin_user
from app.models.schedule import create_schedule
from app.models.schedule_category import create_schedule_category
from app.models.category import join_org_and_to_dict
from contextlib import contextmanager

users_bp = Blueprint("users", __name__)

@users_bp.route("/get_user_id", methods=["GET"])
def get_user_id():
    with SessionLocal() as db:
        try:
            clerk_id = request.args.get("clerk_id")
            if not clerk_id:
                return jsonify({"error": "Missing clerk_id"}), 400
            
            user = get_user_by_clerk_id(db, clerk_id)
            if user is None:
                return jsonify({"error": "User not found"}), 404
            
            return jsonify({"user_id": user.id}), 200
        except Exception as e:
            db.rollback()
            import traceback
            print("❌ Exception:", traceback.format_exc())
            return jsonify({"error": str(e)}), 500


@users_bp.route("/login", methods=["POST"])
def handle_login():
    with SessionLocal() as db:
        try:
            data = request.get_json()
            clerk_id = data.get("clerk_id")
            email = data.get("email")
            fname = data.get("fname")
            lname = data.get("lname")

            if not clerk_id or not email:
                return jsonify({"error": "Missing clerk_id or email"}), 400

            user = get_user_by_clerk_id(db, clerk_id)
            if user is None:
                create_user(
                    db, clerk_id,
                    email=email,
                    fname=fname,
                    lname=lname
                )
                # re-fetch to get the DB-generated _id and calendar_id
                user = get_user_by_clerk_id(db, clerk_id)
                # print("→ Created user:", user)
                # print("→ Dict:", user_to_dict(user))

            if not user.calendar_id:
                # create a new calendar for the user
                creds = fetch_user_credentials()
                if not creds:
                    return jsonify({"error": "Google account not authorized"}), 401

                calendar_id = create_cmucal_calendar(creds)
                update_user_calendar_id(db, clerk_id, calendar_id)
                user = get_user_by_clerk_id(db, clerk_id)

                return jsonify({"status": "created", "user": user_to_dict(user)}), 201

            return jsonify({"status": "exists", "user": user_to_dict(user)}), 200
        except Exception as e:
            db.rollback()
            import traceback
            print("❌ Exception:", traceback.format_exc())
            return jsonify({"error": str(e)}), 500

@users_bp.route("/create_schedule", methods=["POST"])
def create_schedule_record():
    with SessionLocal() as db:
        try:
            data = request.get_json()
            user_id = data.get("user_id")
            name = data.get("name")
            if not user_id or not name:
                return jsonify({"error": "Missing user_id or name"}), 400
            
            schedule = create_schedule(db, user_id=user_id, name=name)

            return jsonify({"status": "schedule created", "user_id": user_id, "schedule_id": schedule.id}), 201
        except Exception as e:
            db.rollback()
            import traceback
            print("❌ Exception:", traceback.format_exc())
            return jsonify({"error": str(e)}), 500

@users_bp.route("/create_schedule_category", methods=["POST"])
def create_schedule_category_record():
    with SessionLocal() as db:
        try:
            data = request.get_json()
            schedule_id = data.get("schedule_id")
            category_id = data.get("category_id")
            if not schedule_id or not category_id:
                return jsonify({"error": "Missing schedule_id or category_id"}), 400
            
            schedule_category = create_schedule_category(db, schedule_id=schedule_id, category_id=category_id)

            return jsonify({"status": "schedule created", "schedule_id": schedule_id, "category_id": category_id}), 201
        except Exception as e:
            db.rollback()
            import traceback
            print("❌ Exception:", traceback.format_exc())
            return jsonify({"error": str(e)}), 500
        

@users_bp.route("/get_admin_categories", methods=["GET"])
def get_admin_categories():
    print("✅ Route /get_admin_categories was called")
    with SessionLocal() as db:
        try:
            clerk_id = request.args.get("clerk_id")
            print("🧩 clerk_id =", clerk_id)

            user = get_user_by_clerk_id(db, clerk_id)
            print("🧩 user_id =", user.id)

            if not user:
                return jsonify({"error": "Missing user_id"}), 400

            categories = get_categories_for_admin_user(db, user.id)
            print(f"🧩 categories fetched: {len(categories)}")

            results = [join_org_and_to_dict(db, category.id) for category in categories]
            print("🧩 results ready:", results)

            return jsonify(results), 200

        except Exception as e:
            db.rollback()
            import traceback
            print("❌ Exception:", traceback.format_exc())
            return jsonify({"error": str(e)}), 500
