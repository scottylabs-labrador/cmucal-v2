from flask import Blueprint, request, jsonify, redirect, current_app
from flask_jwt_extended import jwt_required, get_jwt_identity
from app.services.jwt_state import create_oauth_state_token, verify_oauth_state_token
from app.models.user import get_access_token_for_user, save_google_token
import requests

google_bp = Blueprint("google", __name__)

@google_bp.route("/oauth/state")
@jwt_required()
def oauth_state():
    user_id = get_jwt_identity()
    state = create_oauth_state_token(user_id)
    return jsonify({"state": state})

@google_bp.route("/oauth/callback")
def oauth_callback():
    code = request.args.get("code")
    state = request.args.get("state")
    user_id = verify_oauth_state_token(state)

    # Exchange code for token
    token_res = requests.post("https://oauth2.googleapis.com/token", data={
        "code": code,
        "client_id": current_app.config["GOOGLE_CLIENT_ID"],
        "client_secret": current_app.config["GOOGLE_CLIENT_SECRET"],
        "redirect_uri": "http://localhost:5001/api/google/oauth/callback",
        "grant_type": "authorization_code"
    })

    token_data = token_res.json()
    save_google_token(user_id, token_data)

    return redirect("http://localhost:3000/upload")

@google_bp.route("/calendar/status")
@jwt_required()
def calendar_status():
    user_id = get_jwt_identity()
    has_token = get_access_token_for_user(user_id) is not None
    return jsonify({"hasAccess": has_token})


