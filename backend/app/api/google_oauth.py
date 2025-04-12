from flask import Blueprint, request, jsonify, redirect, current_app
# from flask_jwt_extended import jwt_required, get_jwt_identity
from app.services.clerk_auth import verify_clerk_token
# from app.services.jwt_state import create_oauth_state_token
from app.services.jwt_state import create_oauth_state_token, verify_oauth_state_token
from app.models.user import get_access_token_for_user, save_google_token
import requests

google_bp = Blueprint("google", __name__)

# @jwt_required()

@google_bp.route("/oauth/state")
def oauth_state():
    print("oauth_state called")
    # user_id = get_jwt_identity()
    # print(f"User ID: {user_id}")
    # state = create_oauth_state_token(user_id)
    # return jsonify({"state": state})

    auth_header = request.headers.get("Authorization", "")
    if not auth_header.startswith("Bearer "):
        return jsonify({"error": "Missing Bearer token"}), 401

    token = auth_header.split(" ")[1]

    try:
        user_id = verify_clerk_token(token)
    except Exception as e:
        return jsonify({"error": f"Invalid token: {str(e)}"}), 401

    state = create_oauth_state_token(user_id)
    return jsonify({"state": state})

@google_bp.route("/oauth/callback")
def oauth_callback():
    code = request.args.get("code")
    state_token = request.args.get("state")

    if not code or not state_token:
        return jsonify({"error": "Missing code or state"}), 400

    try:
        user_id = verify_oauth_state_token(state_token)
    except Exception as e:
        return jsonify({"error": f"Invalid state token: {str(e)}"}), 401

    # Exchange code for token
    token_res = requests.post("https://oauth2.googleapis.com/token", data={
        "code": code,
        "client_id": current_app.config["GOOGLE_CLIENT_ID"],
        "client_secret": current_app.config["GOOGLE_CLIENT_SECRET"],
        "redirect_uri": "http://localhost:5001/api/google/oauth/callback",  # match what you used earlier
        "grant_type": "authorization_code",
    })

    if not token_res.ok:
        return jsonify({"error": "Failed to exchange code for token"}), 500

    token_data = token_res.json()
    save_google_token(user_id, token_data)

    return redirect("http://localhost:3000/upload")

@google_bp.route("/calendar/status")
# @jwt_required()
def calendar_status():
    auth_header = request.headers.get("Authorization", "")
    if not auth_header.startswith("Bearer "):
        return jsonify({"error": "Missing token"}), 401

    token = auth_header.split(" ")[1]
    try:
        user_id = verify_clerk_token(token)
    except Exception as e:
        return jsonify({"error": f"Invalid token: {str(e)}"}), 401

    has_token = get_access_token_for_user(user_id) is not None
    return jsonify({"hasAccess": has_token})


