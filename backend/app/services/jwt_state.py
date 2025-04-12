import datetime
from flask import current_app
import jwt  # PyJWT

def create_oauth_state_token(user_id: str) -> str:
    """
    Creates a short-lived JWT used as the 'state' parameter in Google OAuth.
    """
    payload = {
        "sub": user_id,
        "iat": datetime.datetime.utcnow(),
        "exp": datetime.datetime.utcnow() + datetime.timedelta(minutes=10),
    }

    secret = current_app.config["JWT_SECRET_KEY"]  # Same as used for jwt_required
    token = jwt.encode(payload, secret, algorithm="HS256")
    return token


def verify_oauth_state_token(state_token: str) -> str:
    """
    Verifies the 'state' JWT and returns the user ID (sub).
    Raises jwt exceptions if invalid or expired.
    """
    secret = current_app.config["JWT_SECRET_KEY"]
    decoded = jwt.decode(state_token, secret, algorithms=["HS256"])
    return decoded["sub"]
