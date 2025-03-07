from flask import Blueprint, request, jsonify
from app.services.auth_service import check_password, create_token, get_user_by_username

auth_bp = Blueprint("auth", __name__)

@auth_bp.route("/login", methods=["POST"])
def login():
    data = request.json
    username, password = data.get("username"), data.get("password")

    user = get_user_by_username(username)
    if not user or not check_password(user["password"], password):
        return jsonify({"msg": "Invalid credentials"}), 401

    token = create_token(user)
    return jsonify(access_token=token)
