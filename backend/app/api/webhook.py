from flask import Blueprint, request, jsonify
from app.models.user import create_user

webhook_bp = Blueprint("webhook", __name__)

@webhook_bp.route("/clerk", methods=["POST"])
def clerk_webhook():
    """ Webhook to assign default role when a new user signs up in Clerk """
    data = request.json
    print("called the webhook")

    if not data or "id" not in data:
        return jsonify({"msg": "Invalid request"}), 400

    clerk_id = data["id"]
    create_user(clerk_id, role="user")  # Assign "user" by default
    print("User role assigned successfully")

    return jsonify({"msg": "User role assigned successfully"}), 200
