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
