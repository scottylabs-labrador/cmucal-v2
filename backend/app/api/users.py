from flask import Blueprint, jsonify, request
from app.models.user import get_user_by_clerk_id, create_user, user_to_dict
# from app.services.google_service import fetch_user_credentials
# from app.models.user import User, update_user_calendar_id
# from app.services.google_service import create_cmucal_calendar
from app.services.db import SessionLocal

users_bp = Blueprint("users", __name__)


@users_bp.route("/login", methods=["POST"])
def handle_login():
    db = SessionLocal()
    try:
        data = request.get_json()
        clerk_id = data.get("clerk_id")
        email = data.get("email")
        first_name = data.get("first_name")
        last_name = data.get("last_name")

        if not clerk_id or not email:
            return jsonify({"error": "Missing clerk_id or email"}), 400

        user = get_user_by_clerk_id(db, clerk_id)
        if user is None:
            create_user(
                db, clerk_id,
                email=email,
                first_name=first_name,
                last_name=last_name
            )
            # re-fetch to get the DB-generated _id and calendar_id
            user = get_user_by_clerk_id(db, clerk_id)
            # print("→ Created user:", user)
            # print("→ Dict:", user_to_dict(user))

            # if not user.get("calendar_id"):
            #     # create a new calendar for the user
            #     creds = fetch_user_credentials()
            #     if not creds:
            #         return jsonify({"error": "Google account not authorized"}), 401

            #     calendar_id = create_cmucal_calendar(creds)
            #     update_user_calendar_id(clerk_id, calendar_id)
            
            #     user["calendar_id"] = calendar_id  # Update response payload
            # print("User:", user)
            # print("Type:", type(user))

            return jsonify({"status": "created", "user": user_to_dict(user)}), 201

        return jsonify({"status": "exists", "user": user_to_dict(user)}), 200
    except Exception as e:
        db.rollback()
        import traceback
        print("❌ Exception:", traceback.format_exc())
        return jsonify({"error": str(e)}), 500
    finally:
        db.close()

