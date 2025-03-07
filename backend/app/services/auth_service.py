# handles authentication logic (JWT, bcrypt)
from flask_bcrypt import Bcrypt
from flask_jwt_extended import create_access_token
from app.models.user import mongo

bcrypt = Bcrypt()

def check_password(hashed_password, password):
    """ Verify password """
    return bcrypt.check_password_hash(hashed_password, password)

def create_token(user):
    """ Generate JWT with role """
    return create_access_token(identity=user["username"], additional_claims={"role": user["role"]})

def get_user_by_username(username):
    """ Retrieve user from MongoDB """
    return mongo.db.users.find_one({"username": username})
