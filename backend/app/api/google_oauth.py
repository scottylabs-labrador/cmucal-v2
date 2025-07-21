# routes requests and coordinates services/models
from flask import Blueprint, request, jsonify, redirect, current_app, session
from app.services.db import SessionLocal

from app.services.google_service import (
    create_google_flow,
    fetch_user_credentials,
    list_user_calendars,
    fetch_events_for_calendars,
    add_event,
    delete_event,
    credentials_to_dict
)
from app.models.google_event import save_google_event, get_google_event_by_local_id, delete_google_event_by_local_id
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

@google_bp.route("/calendar/status")
def calendar_status():
    return jsonify({ "authorized": "credentials" in session })

@google_bp.route("/calendars")
def calendars():
    creds = fetch_user_credentials()
    if not creds:
        return jsonify({"error": "Unauthorized"}), 401
    return jsonify(list_user_calendars(creds))

@google_bp.route("/calendar/events/bulk", methods=["POST"])
def bulk_events():
    creds = fetch_user_credentials()
    if not creds:
        return jsonify({"error": "Unauthorized"}), 401
    calendar_ids = request.get_json().get("calendarIds", [])
    return jsonify(fetch_events_for_calendars(creds, calendar_ids))

import traceback
from datetime import datetime
def convert_to_iso8601(dt_str):
    return datetime.strptime(dt_str, "%a, %d %b %Y %H:%M:%S %Z").isoformat() + "Z"
    # will move this somewhere else when refactoring

@google_bp.route("/calendar/events/add", methods=["POST"])
def add_event_route():
    db = SessionLocal()
    try:
        creds = fetch_user_credentials()
        if not creds:
            return jsonify({"error": "Unauthorized"}), 401

        data = request.get_json()

        clerk_id = data.get("user_id")
        if not clerk_id:
            return jsonify({"error": "Missing user_id"}), 400

        user = get_user_by_clerk_id(db, clerk_id)
        if not user or not user.calendar_id:
            return jsonify({"error": "User or calendar not found"}), 400

        calendar_id = user.calendar_id
        data["start"] = convert_to_iso8601(data["start"]) # data["start"].isoformat()
        data["end"] = convert_to_iso8601(data["end"]) # data["end"].isoformat()

        event = add_event(creds, data, calendar_id)

        save_google_event(
            db=db,
            user_id=user.id,
            local_event_id=data["local_event_id"],
            google_event_id=event["id"],
            title=data["title"],
            start=data["start"],
            end=data["end"]
        )

        return jsonify({ "googleEventId": event["id"] })

    except Exception as e:
        db.rollback()
        return jsonify({ "error": str(e) }), 500
    finally:
        db.close()
    

@google_bp.route("/calendar/events/<local_event_id>", methods=["DELETE"])
def delete_event_route(local_event_id):
    db = SessionLocal()
    try:
        creds = fetch_user_credentials()
        if not creds:
            return jsonify({"error": "Unauthorized"}), 401

        data = request.get_json(force=True)
        user_id = data.get("user_id")
        if not user_id:
            return jsonify({"error": "Missing user_id"}), 400
        
        user = get_user_by_clerk_id(db, user_id)
        if not user or not user.calendar_id:
            return jsonify({"error": "User or calendar not found"}), 400

        record = get_google_event_by_local_id(db, user.id, local_event_id)
        if not record:
            return jsonify({ "error": "No matching event found" }), 404

        calendar_id = user.calendar_id

        delete_event(creds, record.google_event_id, calendar_id)
        delete_google_event_by_local_id(db, user.id, local_event_id)

        return jsonify({ "status": "deleted" })

    except Exception as e:
        db.rollback()
        return jsonify({ "error": str(e) }), 500
    finally:
        db.close()
