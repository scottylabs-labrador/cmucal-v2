from flask import Blueprint, session, jsonify, redirect
from flask_jwt_extended import jwt_required, get_jwt
from app.services.google_service import get_google_calendar_service, fetch_calendar_events

admin_bp = Blueprint("admin", __name__)

@admin_bp.route("/calendar/auth", methods=["GET"])
@jwt_required()
def google_auth():
    """ Redirects admin to Google OAuth login """
    claims = get_jwt()
    if claims["role"] != "admin":
        return jsonify({"msg": "Unauthorized"}), 403
    return redirect(get_google_calendar_service())

@admin_bp.route("/calendar/callback", methods=["GET"])
def google_auth_callback():
    """ Handles Google OAuth callback and stores credentials """
    flow = google_auth_oauthlib.flow.Flow.from_client_secrets_file(
        Config.GOOGLE_CLIENT_SECRET_FILE, scopes=Config.GOOGLE_SCOPES
    )
    flow.redirect_uri = url_for("google_auth_callback", _external=True)
    flow.fetch_token(authorization_response=request.url)

    session["google_credentials"] = flow.credentials_to_dict()
    return jsonify({"msg": "Google Authentication Successful!"})

@admin_bp.route("/calendar/events", methods=["GET"])
@jwt_required()
def get_calendar_events():
    """ Fetch events from Google Calendar (Admin only) """
    claims = get_jwt()
    if claims["role"] != "admin":
        return jsonify({"msg": "Unauthorized"}), 403

    if "google_credentials" not in session:
        return jsonify({"msg": "Google Authentication Required"}), 401

    events = fetch_calendar_events()
    return jsonify(events)
