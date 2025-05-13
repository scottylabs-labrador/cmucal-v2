from flask import Blueprint, request, jsonify, redirect, current_app, session, url_for
from google_auth_oauthlib.flow import Flow
from googleapiclient.discovery import build
from google.oauth2.credentials import Credentials
from datetime import datetime
from datetime import timedelta

from app.models.google_event import save_google_event
from app.models.google_event import get_google_event_by_local_id, delete_google_event_by_local_id


# from app.models.user import get_access_token_for_user, save_google_token
# import requests

google_bp = Blueprint("google", __name__)

SCOPES = ["https://www.googleapis.com/auth/calendar.events", "https://www.googleapis.com/auth/userinfo.email", 
          "https://www.googleapis.com/auth/calendar", "openid", "https://www.googleapis.com/auth/calendar.readonly"]

@google_bp.route("/authorize")
def authorize():
    session.pop("credentials", None)
    redirect_url = request.args.get("redirect", "http://localhost:3000")
    flow = Flow.from_client_config(
        {
            "web": {
                "client_id": current_app.config["GOOGLE_CLIENT_ID"],
                "client_secret": current_app.config["GOOGLE_CLIENT_SECRET"],
                "redirect_uris": current_app.config["GOOGLE_REDIRECT_URI"],
                "auth_uri": "https://accounts.google.com/o/oauth2/auth",
                "token_uri": "https://oauth2.googleapis.com/token",
            }
        },
        scopes=SCOPES,
    )
    flow.redirect_uri = current_app.config["GOOGLE_REDIRECT_URI"]
    authorization_url, state = flow.authorization_url(
        access_type="offline",
        include_granted_scopes="true",
        prompt="consent"  # force refresh_token to be issued every time
    )

    session["state"] = state
    session["post_auth_redirect"] = redirect_url  # save redirect location
    return redirect(authorization_url)

@google_bp.route("/oauth/callback")
def oauth2callback():
    state = session["state"]
    flow = Flow.from_client_config(
        {
            "web": {
                "client_id": current_app.config["GOOGLE_CLIENT_ID"],
                "client_secret": current_app.config["GOOGLE_CLIENT_SECRET"],
                "redirect_uris": current_app.config["GOOGLE_REDIRECT_URI"],
                "auth_uri": "https://accounts.google.com/o/oauth2/auth",
                "token_uri": "https://oauth2.googleapis.com/token",
            }
        },
        scopes=SCOPES,
        state=state,
    )
    flow.redirect_uri = current_app.config["GOOGLE_REDIRECT_URI"]
    flow.fetch_token(authorization_response=request.url)

    credentials = flow.credentials
    session["credentials"] = {
       "token": credentials.token,
        "refresh_token": credentials.refresh_token,
        "token_uri": credentials.token_uri,
        "client_id": credentials.client_id,
        "client_secret": credentials.client_secret,
        "scopes": credentials.scopes,
    }
    frontend_url = current_app.config["FRONTEND_REDIRECT_URI"]
    redirect_target = session.pop("post_auth_redirect", frontend_url)
    return redirect(redirect_target)  # React frontend

@google_bp.route("/calendar/status")
def calendar_status():
    has_creds = "credentials" in session
    return jsonify({ "authorized": has_creds })

def get_credentials():
    creds_data = session.get("credentials")
    if not creds_data:
        return None
    return Credentials(**creds_data)

@google_bp.route("/calendars")
def list_calendars():
    creds = get_credentials()
    if not creds:
        return jsonify({"error": "Unauthorized"}), 401

    service = build("calendar", "v3", credentials=creds)
    calendar_list = service.calendarList().list().execute()
    return jsonify(calendar_list["items"])

@google_bp.route("/calendar/events/bulk", methods=["POST"])
def fetch_bulk_events():
    data = request.get_json()
    calendar_ids = data.get("calendarIds", [])

    creds = get_credentials()
    service = build("calendar", "v3", credentials=creds)

    all_events = []

    # Define the reference date
    reference_date = datetime.now()

    # Calculate three months before and after
    time_min = (reference_date - timedelta(days=90)).isoformat() + "Z"
    time_max = (reference_date + timedelta(days=90)).isoformat() + "Z"

    for cal_id in calendar_ids:
        res = (
            service.events()
            .list(
                calendarId=cal_id,
                timeMin=time_min, # 3 months before now
                timeMax=time_max, # 3 months from now
                singleEvents=True,
                orderBy="startTime",
            )
            .execute()
        )
        for event in res.get("items", []):
            start = event["start"]
            end = event["end"]
            is_all_day = "date" in start  # all-day if 'date' is used instead of 'dateTime'

            all_events.append({
                "title": event.get("summary", "No Title"),
                "start": start.get("dateTime") or start.get("date"),
                "end": end.get("dateTime") or end.get("date"),
                "allDay": is_all_day,
                "calendarId": cal_id,
            })

    return jsonify(all_events)

@google_bp.route("/calendar/events/add", methods=["POST"])
def add_event_to_calendar():
    creds = get_credentials()
    if not creds:
        return jsonify({"error": "Unauthorized"}), 401

    data = request.get_json()
    event_data = {
        "summary": data["title"],
        "start": {"dateTime": data["start"], "timeZone": "America/New_York"},
        "end": {"dateTime": data["end"], "timeZone": "America/New_York"},
    }

    service = build("calendar", "v3", credentials=creds)
    event = service.events().insert(calendarId="primary", body=event_data).execute()

    save_google_event(
        user_id=data["user_id"],  # or however you track logged-in users
        local_event_id=data["local_event_id"],
        google_event_id=event["id"],
        title=data["title"],
        start=data["start"],
        end=data["end"]
    )

    return jsonify({ "googleEventId": event["id"] })

@google_bp.route("/calendar/events/<local_event_id>", methods=["DELETE"])
def delete_event_from_calendar(local_event_id):
    creds = get_credentials()
    if not creds:
        return jsonify({"error": "Unauthorized"}), 401

    try:
        data = request.get_json(force=True) or {}
        user_id = data.get("user_id")
        if not user_id:
            return jsonify({"error": "Missing user_id"}), 400

        print(f"Deleting event {local_event_id} for user {user_id}")

        # Look up Google event ID
        record = get_google_event_by_local_id(user_id=user_id, local_event_id=local_event_id)
        if not record:
            return jsonify({ "error": "No matching event found" }), 404

        google_event_id = record["google_event_id"]

        # Delete from Google Calendar
        try:
            service = build("calendar", "v3", credentials=creds)
            service.events().delete(calendarId="primary", eventId=google_event_id).execute()
        except Exception as google_error:
            print("Google API error:", google_error)
            return jsonify({"error": "Failed to delete from Google Calendar"}), 500

        # Delete from DB
        delete_google_event_by_local_id(user_id=user_id, local_event_id=local_event_id)

        return jsonify({ "status": "deleted" })
    except Exception as e:
        print("Unexpected error:", e)
        return jsonify({ "error": str(e) }), 500
