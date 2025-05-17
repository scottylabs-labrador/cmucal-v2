# handles API logic (Google Calendar)
from google_auth_oauthlib.flow import Flow
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build
from flask import session
from datetime import datetime, timedelta, timezone


SCOPES = [
    "https://www.googleapis.com/auth/calendar.events",
    "https://www.googleapis.com/auth/userinfo.email",
    "https://www.googleapis.com/auth/calendar",
    "openid",
    "https://www.googleapis.com/auth/calendar.readonly"
]

def create_google_flow(config, state=None):
    flow = Flow.from_client_config(
        {
            "web": {
                "client_id": config["GOOGLE_CLIENT_ID"],
                "client_secret": config["GOOGLE_CLIENT_SECRET"],
                "redirect_uris": config["GOOGLE_REDIRECT_URI"],
                "auth_uri": "https://accounts.google.com/o/oauth2/auth",
                "token_uri": "https://oauth2.googleapis.com/token",
            }
        },
        scopes=SCOPES,
        state=state
    )
    flow.redirect_uri = config["GOOGLE_REDIRECT_URI"]
    return flow

def fetch_user_credentials():
    creds_data = session.get("credentials")
    return Credentials(**creds_data) if creds_data else None

def build_calendar_service(credentials):
    return build("calendar", "v3", credentials=credentials)

def list_user_calendars(credentials):
    service = build_calendar_service(credentials)
    return service.calendarList().list().execute()["items"]



def fetch_events_for_calendars(credentials, calendar_ids):
    service = build_calendar_service(credentials)
    now = datetime.utcnow() # don't change this, changing will cause error!
    time_min = (now - timedelta(days=90)).isoformat() + "Z"
    time_max = (now + timedelta(days=90)).isoformat() + "Z"
    all_events = []

    for cal_id in calendar_ids:
        try:
            res = service.events().list(
                calendarId=cal_id,
                timeMin=time_min,
                timeMax=time_max,
                singleEvents=True,
                orderBy="startTime"
            ).execute()
            for event in res.get("items", []):
                start = event["start"]
                end = event["end"]
                is_all_day = "date" in start
                all_events.append({
                    "title": event.get("summary", "No Title"),
                    "start": start.get("dateTime") or start.get("date"),
                    "end": end.get("dateTime") or end.get("date"),
                    "allDay": is_all_day,
                    "calendarId": cal_id,
                })
        except Exception as e:
            print(f"Error fetching calendar {cal_id}: {e}")
            continue
    return all_events

def add_event(credentials, data, calendar_id):
    service = build_calendar_service(credentials)
    event_data = {
        "summary": data["title"],
        "start": {"dateTime": data["start"], "timeZone": "America/New_York"},
        "end": {"dateTime": data["end"], "timeZone": "America/New_York"},
    }
    # "primary"
    return service.events().insert(calendarId=calendar_id, body=event_data).execute()

def delete_event(credentials, event_id, calendar_id):
    service = build_calendar_service(credentials)
    service.events().delete(calendarId=calendar_id, eventId=event_id).execute()

def create_cmucal_calendar(credentials):
    service = build("calendar", "v3", credentials=credentials)
    calendar = {
        "summary": "CMUCal",
        "timeZone": "America/New_York"
    }
    created_calendar = service.calendars().insert(body=calendar).execute()
    return created_calendar["id"]

def credentials_to_dict(credentials):
    return {
        "token": credentials.token,
        "refresh_token": credentials.refresh_token,
        "token_uri": credentials.token_uri,
        "client_id": credentials.client_id,
        "client_secret": credentials.client_secret,
        "scopes": credentials.scopes,
    }

