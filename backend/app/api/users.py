from flask import Blueprint, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity

users_bp = Blueprint("users", __name__)

@users_bp.route("/profile", methods=["GET"])
@jwt_required()
def profile():
    user = get_jwt_identity()
    return jsonify({"msg": f"Hello, {user}!"})
