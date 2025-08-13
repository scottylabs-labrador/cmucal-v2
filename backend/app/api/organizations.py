from flask import Blueprint, jsonify, request
from app.models.user import get_user_by_clerk_id, create_user, user_to_dict
from app.services.google_service import fetch_user_credentials
from app.models.user import update_user_calendar_id
from app.services.google_service import create_cmucal_calendar
from app.services.db import SessionLocal
from app.models.organization import create_organization, get_orgs_by_type
from app.models.models import Organization
from app.models.admin import create_admin
from app.models.category import create_category
from app.utils.course_data import get_course_data



orgs_bp = Blueprint("orgs", __name__)

@orgs_bp.route("/get_course_orgs", methods=["GET"])
def get_course_orgs():
    with SessionLocal() as db:
        try:
            orgs = get_orgs_by_type(db, org_type='COURSE')
            if not orgs:
                return jsonify({"error": "No course organizations found"}), 404
            orgs_list = []
            for org in orgs:
                parts = org.name.split(" ")
                course_num = parts[0]
                course_title = " ".join(parts[1:])
                orgs_list.append({
                    "id": org.id,
                    "number": course_num,
                    "title": course_title,
                    "label": org.name,
                })

            return jsonify(orgs_list), 200
        except Exception as e:
            db.rollback()
            import traceback
            print("❌ Exception:", traceback.format_exc())
            return jsonify({"error": str(e)}), 500

@orgs_bp.route("/get_club_orgs", methods=["GET"])
def get_club_orgs():
    with SessionLocal() as db:
        try:
            # Debug: Check all organizations first
            all_orgs = db.query(Organization).all()
            print(f"Total organizations in database: {len(all_orgs)}")
            for org in all_orgs[:5]:  # Print first 5 for debugging
                print(f"Org ID: {org.id}, Name: {org.name}, Type: {org.type}")
            
            orgs = get_orgs_by_type(db, org_type='CLUB')
            print(f"Found {len(orgs)} CLUB organizations")
            
            if not orgs:
                # Return empty list instead of 404 for better UX
                return jsonify([]), 200
                
            orgs_list = []
            for org in orgs:
                orgs_list.append({
                    "id": org.id,
                    "name": org.name,
                    "description": org.description,
                })

            return jsonify(orgs_list), 200
        except Exception as e:
            db.rollback()
            import traceback
            print("❌ Exception:", traceback.format_exc())
            return jsonify({"error": str(e)}), 500

@orgs_bp.route("/get_courses", methods=["GET"])
def get_courses_from_soc():
    """
    Endpoint to fetch course data from the JSON file.
    To update the JSON file, follow the instructions in the README in the rust directory.
    """
    try:
        courses = get_course_data()
        return jsonify(courses), 200
    except FileNotFoundError as e:
        return jsonify({"error": str(e)}), 404
    except Exception as e:
        return jsonify({"error": "An error occurred while fetching course data."}), 500




@orgs_bp.route("/create_org", methods=["POST"])
def create_org_record():
    with SessionLocal() as db:
        try:
            data = request.get_json()
            org_name = data.get("name")
            org_description = data.get("description", None)
            org_type = data.get("type", None)
            if not org_name:
                return jsonify({"error": "Missing org_name"}), 400

            org = create_organization(db, name=org_name, description=org_description, type=org_type)

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

@orgs_bp.route("/create_test_clubs", methods=["POST"])
def create_test_clubs():
    """Create some test club organizations for development"""
    with SessionLocal() as db:
        try:
            test_clubs = [
                {"name": "ScottyLabs", "description": "A community of passionate, interdisciplinary leaders that use design and technology to achieve more."},
                {"name": "UXA", "description": "User Experience Association - Exploring the intersection of design and technology"},
                {"name": "Activities Board", "description": "Programming events and activities for the CMU community"},
                {"name": "Badminton Club", "description": "CMU Badminton Club for recreational and competitive play"},
                {"name": "Robotics Club", "description": "Building and programming robots for competitions and fun"},
                {"name": "Photography Club", "description": "Capturing moments and exploring creative photography"}
            ]
            
            created_clubs = []
            for club_data in test_clubs:
                # Check if club already exists
                existing = db.query(Organization).filter(
                    Organization.name == club_data["name"],
                    Organization.type == "CLUB"
                ).first()
                
                if not existing:
                    org = create_organization(db, 
                                            name=club_data["name"], 
                                            description=club_data["description"], 
                                            type="CLUB")
                    created_clubs.append(org.name)
            
            return jsonify({
                "status": "success", 
                "created_clubs": created_clubs,
                "message": f"Created {len(created_clubs)} new clubs"
            }), 201
            
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

