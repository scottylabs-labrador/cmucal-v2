from flask import Blueprint, jsonify, request
from app.models.user import get_user_by_clerk_id, create_user, user_to_dict
from app.services.google_service import fetch_user_credentials
from app.models.user import update_user_calendar_id
from app.services.google_service import create_cmucal_calendar
from app.services.db import SessionLocal
from app.models.organization import create_organization
from app.models.admin import create_admin
from app.models.category import create_category


orgs_bp = Blueprint("orgs", __name__)


@orgs_bp.route("/create_org", methods=["POST"])
def create_org_record():
    with SessionLocal() as db:
        try:
            data = request.get_json()
            org_name = data.get("name")
            org_description = data.get("description", None)
            if not org_name:
                return jsonify({"error": "Missing org_name"}), 400
            
            org = create_organization(db, name=org_name, description=org_description)

            return jsonify({"status": "created", "org_id": org.id}), 201
        except Exception as e:
            db.rollback()
            import traceback
            print("❌ Exception:", traceback.format_exc())
            return jsonify({"error": str(e)}), 500

@orgs_bp.route("/create_category", methods=["POST"])
def create_category_record():
    with SessionLocal() as db:
        try:
            data = request.get_json()
            org_id = data.get("org_id")
            if not org_id:
                return jsonify({"error": "Missing org_id"}), 400
            name = data.get("name")
            if not name:
                return jsonify({"error": "Missing category name"}), 400
            
            category = create_category(db, org_id=org_id, name=name)
            
            return jsonify({"status": "category created", "category_id": category.id}), 201
        except Exception as e:
            db.rollback()
            import traceback
            print("❌ Exception:", traceback.format_exc())
            return jsonify({"error": str(e)}), 500

@orgs_bp.route("/create_admin", methods=["POST"])
def create_admin_record():
    with SessionLocal() as db:
        try:
            data = request.get_json()
            user_id = data.get("user_id")
            if not user_id:
                return jsonify({"error": "Missing user_id"}), 400
            org_id = data.get("org_id")
            if not org_id:
                return jsonify({"error": "Missing org_id"}), 400
            role = data.get("role", "admin")
            category_id = data.get("category_id", None)
            
            
            admin = create_admin(db, org_id=org_id, user_id=user_id, role=role, category_id=category_id)
            
            return jsonify({"status": "admin created", "user": admin.user_id, "org": admin.org_id}), 200
        except Exception as e:
            db.rollback()
            import traceback
            print("❌ Exception:", traceback.format_exc())
            return jsonify({"error": str(e)}), 500

