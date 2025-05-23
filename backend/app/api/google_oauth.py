# routes requests and coordinates services/models
from flask import Blueprint, request, jsonify, redirect, current_app, session

from app.services.google_service import (
    create_google_flow,
    fetch_user_credentials,
    list_user_calendars,
    fetch_events_for_calendars,
    add_event,
    delete_event,
    credentials_to_dict
)
# from app.models.google_event import save_google_event, get_google_event_by_local_id, delete_google_event_by_local_id
from app.models.user import get_user_by_clerk_id

google_bp = Blueprint("google", __name__)




@google_bp.route("/authorize")
def authorize():
    session.pop("credentials", None)
    redirect_url = request.args.get("redirect", "http://localhost:3000")
    flow = create_google_flow(current_app.config)
    authorization_url, state = flow.authorization_url(
        access_type="offline",
        include_granted_scopes="true",
        prompt="consent"
    )
    session["state"] = state
    session["post_auth_redirect"] = redirect_url
    return redirect(authorization_url)

@google_bp.route("/oauth/callback")
def oauth2callback():
    state = session["state"]
    flow = create_google_flow(current_app.config, state)
    flow.fetch_token(authorization_response=request.url)
    session["credentials"] = credentials_to_dict(flow.credentials)
    return redirect(session.pop("post_auth_redirect", current_app.config["FRONTEND_REDIRECT_URI"]))

# @google_bp.route("/calendar/status")
def calendar_status():
    return jsonify({ "authorized": "credentials" in session })

# @google_bp.route("/calendars")
def calendars():
    creds = fetch_user_credentials()
    if not creds:
        return jsonify({"error": "Unauthorized"}), 401
    return jsonify(list_user_calendars(creds))

# @google_bp.route("/calendar/events/bulk", methods=["POST"])
# def bulk_events():
#     creds = fetch_user_credentials()
#     if not creds:
#         return jsonify({"error": "Unauthorized"}), 401
#     calendar_ids = request.get_json().get("calendarIds", [])
#     return jsonify(fetch_events_for_calendars(creds, calendar_ids))

# @google_bp.route("/calendar/events/add", methods=["POST"])
# def add_event_route():
#     creds = fetch_user_credentials()
#     if not creds:
#         return jsonify({"error": "Unauthorized"}), 401
#     data = request.get_json()

#     user = get_user_by_clerk_id(data["user_id"])
#     if not user or "calendar_id" not in user:
#         return jsonify({"error": "User or calendar not found"}), 400

#     calendar_id = user["calendar_id"]

#     event = add_event(creds, data, calendar_id)
#     save_google_event(
#         user_id=data["user_id"],
#         local_event_id=data["local_event_id"],
#         google_event_id=event["id"],
#         title=data["title"],
#         start=data["start"],
#         end=data["end"]
#     )

#     return jsonify({ "googleEventId": event["id"] })

# @google_bp.route("/calendar/events/<local_event_id>", methods=["DELETE"])
# def delete_event_route(local_event_id):
#     creds = fetch_user_credentials()
#     if not creds:
#         return jsonify({"error": "Unauthorized"}), 401
#     user_id = request.get_json(force=True).get("user_id")
#     if not user_id:
#         return jsonify({"error": "Missing user_id"}), 400

#     record = get_google_event_by_local_id(user_id, local_event_id)
#     if not record:
#         return jsonify({ "error": "No matching event found" }), 404

#     user = get_user_by_clerk_id(user_id)
#     if not user or "calendar_id" not in user:
#         return jsonify({"error": "User or calendar not found"}), 400

#     calendar_id = user["calendar_id"]

#     delete_event(creds, record["google_event_id"], calendar_id)
#     delete_google_event_by_local_id(user_id, local_event_id)
#     return jsonify({ "status": "deleted" })
