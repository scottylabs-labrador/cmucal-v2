from flask import Blueprint, jsonify, request
from app.models.user import get_user_by_clerk_id, create_user

users_bp = Blueprint("users", __name__)

@users_bp.route("/login", methods=["POST"])
def handle_login():
    data = request.get_json()
    clerk_id = data.get("clerk_id")
    email = data.get("email")
    first_name = data.get("first_name")
    last_name = data.get("last_name")

    if not clerk_id or not email:
        return jsonify({"error": "Missing clerk_id or email"}), 400

    user = get_user_by_clerk_id(clerk_id)
    if user is None:
        user = create_user(clerk_id, email, first_name, last_name)
        return jsonify({"status": "created", "user": user}), 201

    return jsonify({"status": "exists", "user": user}), 200
