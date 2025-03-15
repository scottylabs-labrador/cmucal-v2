from flask import Blueprint, request, jsonify
from app.services.auth_service import verify_clerk_token
from app.models.user import get_user_role

auth_bp = Blueprint("auth", __name__)

@auth_bp.route("/role", methods=["GET"])
def get_role():
    """ Verify Clerk JWT and return user role """
    clerk_user = verify_clerk_token()
    if not clerk_user:
        return jsonify({"msg": "Unauthorized"}), 401

    clerk_id = clerk_user["id"]
    role = get_user_role(clerk_id)
    return jsonify({"role": role})
