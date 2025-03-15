import requests
from flask import request, jsonify
from app.models.user import get_user_role
import os

CLERK_SECRET_KEY = os.getenv("CLERK_SECRET_KEY")  # Get this from Clerk Dashboard


def verify_clerk_token():
    """ Verify Clerk JWT and extract user info """
    auth_header = request.headers.get("Authorization")
    if not auth_header or not auth_header.startswith("Bearer "):
        return None

    token = auth_header.split(" ")[1]
    headers = {"Authorization": f"Bearer {CLERK_SECRET_KEY}"}

    response = requests.get("https://api.clerk.dev/v1/me", headers=headers)
    if response.status_code != 200:
        return None

    return response.json()  # Returns user details from Clerk

def role_required(role):
    """ Decorator to restrict routes based on user role """
    def wrapper(func):
        def decorated_function(*args, **kwargs):
            clerk_user = verify_clerk_token()
            if not clerk_user:
                return jsonify({"msg": "Unauthorized"}), 401

            clerk_id = clerk_user["id"]
            user_role = get_user_role(clerk_id)
            if user_role != role:
                return jsonify({"msg": "Forbidden"}), 403

            return func(*args, **kwargs)
        return decorated_function
    return wrapper

