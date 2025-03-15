# import os
# import google.oauth2.credentials
# import google_auth_oauthlib.flow
# import googleapiclient.discovery
# from flask import url_for, redirect, session
# from app.config.settings import Config

# def get_google_calendar_service():
#     """ Authenticate and return a Google Calendar API service instance """
#     flow = google_auth_oauthlib.flow.Flow.from_client_secrets_file(
#         Config.GOOGLE_CLIENT_SECRET_FILE, scopes=Config.GOOGLE_SCOPES
#     )
#     flow.redirect_uri = url_for("google_auth_callback", _external=True)

#     auth_url, state = flow.authorization_url(access_type="offline", prompt="consent")
#     session["state"] = state
#     return auth_url

# def fetch_calendar_events():
#     """ Retrieve Google Calendar events """
#     credentials = google.oauth2.credentials.Credentials(**session["google_credentials"])
#     service = googleapiclient.discovery.build("calendar", "v3", credentials=credentials)

#     events_result = service.events().list(calendarId="primary", maxResults=10).execute()
#     events = events_result.get("items", [])
#     return events
