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
