from flask import current_app
from app.services.db import mongo


def create_user(data, role="user"):
    """ Automatically assign 'user' role when a new Clerk user registers """
    db = mongo.cx["CMUCal"]
    # print("Mongo client in create_user: ", db)
    if db is None:
        print("Mongo not initialized")
        return
    clerk_id = data.get("id")
    existing_user = db.users.find_one({"clerk_id": clerk_id})
    print("clerk_id in create_user: ", clerk_id)
    if not existing_user:
        user = {"clerk_id": clerk_id, "role": role, "first_name": data.get("first_name"), "last_name": data.get("last_name")}
        result = db.users.insert_one(user)
        print("User created with ID:", result.inserted_id)

def get_user_role(clerk_id):
    """ Retrieve user role from MongoDB """

    db = mongo.cx["CMUCal"]  # Get `mongo` from Flask context
    user = db.users.find_one({"clerk_id": clerk_id})
    return user["role"] if user else None


# Save token data from Google (access_token, refresh_token, expiry, etc.)
def save_google_token(user_id: str, token_data: dict):
    """
    Store Google OAuth token info in user's record.
    """
    db = mongo.cx["CMUCal"]
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
    db = mongo.cx["CMUCal"]
    user = db.users.find_one({"clerk_id": user_id}, {"google_oauth.access_token": 1})
    return user.get("google_oauth", {}).get("access_token") if user else None
