from flask import current_app
from app.services.db import get_db

def update_user_calendar_id(clerk_id, calendar_id):
    db = get_db()
    db["users"].update_one(
        { "clerk_id": clerk_id },
        { "$set": { "calendar_id": calendar_id } }
    )

def get_user_by_clerk_id(clerk_id: str):
    db = get_db()
    users_collection = db["users"]
    return users_collection.find_one({"clerk_id": clerk_id})


def create_user(clerk_id: str, email: str, first_name: str = "", last_name: str = ""):
    db = get_db()
    users_collection = db["users"]
    
    user_data = {
        "clerk_id": clerk_id,
        "email": email,
        "first_name": first_name,
        "last_name": last_name,
    }
    
    users_collection.insert_one(user_data)
    return user_data


def get_user_role(clerk_id):
    """ Retrieve user role from MongoDB """

    db = get_db()  # Get `mongo` from Flask context
    user = db.users.find_one({"clerk_id": clerk_id})
    return user["role"] if user else None


# Save token data from Google (access_token, refresh_token, expiry, etc.)
def save_google_token(user_id: str, token_data: dict):
    """
    Store Google OAuth token info in user's record.
    """
    db = get_db()
    db.users.update_one(
        {"clerk_id": user_id},
        {
            "$set": {
                "google_oauth": {
                    "access_token": token_data.get("access_token"),
                    "refresh_token": token_data.get("refresh_token"),
                    "expires_in": token_data.get("expires_in"),
                    "scope": token_data.get("scope"),
                    "token_type": token_data.get("token_type"),
                    "id_token": token_data.get("id_token"),
                }
            }
        },
        upsert=True
    )

# Retrieve Google access token (returns None if not set)
def get_access_token_for_user(user_id: str):
    """
    Fetch the user's Google access token if it exists.
    """
    db = get_db()
    user = db.users.find_one({"clerk_id": user_id}, {"google_oauth.access_token": 1})
    return user.get("google_oauth", {}).get("access_token") if user else None
