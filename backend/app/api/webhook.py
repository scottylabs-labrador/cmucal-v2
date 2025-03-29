from flask import Blueprint, request, jsonify
from app.models.user import create_user

webhook_bp = Blueprint("webhook", __name__)

@webhook_bp.route("/clerk", methods=["POST"])
def clerk_webhook():
    """ Webhook to assign default role when a new user signs up in Clerk """
    data = request.json
    print("called the webhook")
    user_data = data.get("data")

    clerk_id = user_data.get("id")
    if not clerk_id:
        return jsonify({"msg": "Invalid payload"}), 400

    create_user(user_data)
    print("User role assigned successfully")

    return jsonify({"msg": "User role assigned successfully"}), 200
