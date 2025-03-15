from flask import current_app
from flask_pymongo import PyMongo

def get_mongo():
    """Retrieve the mongo instance from Flask's app context"""
    return PyMongo(current_app)

def create_user(clerk_id, role="user"):
    """ Automatically assign 'user' role when a new Clerk user registers """
    mongo = get_mongo()  # Get `mongo` from Flask context


    if mongo.db is None:
        print("ERROR: mongo.db is None. Check if MongoDB is connected properly.")
        return


    existing_user = mongo.db.users.find_one({"clerk_id": clerk_id})
    print("clerk_id in create_user: ", clerk_id)
    if not existing_user:
        user = {"clerk_id": clerk_id, "role": role}
        result = mongo.db.users.insert_one(user)
        print("User created with ID:", result.inserted_id)

def get_user_role(clerk_id):
    """ Retrieve user role from MongoDB """

    mongo = get_mongo()  # Get `mongo` from Flask context
    user = mongo.db.users.find_one({"clerk_id": clerk_id})
    return user["role"] if user else None
