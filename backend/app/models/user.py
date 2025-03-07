from flask_pymongo import PyMongo

mongo = PyMongo()

def create_user(username, password, role):
    """ Insert a new user into MongoDB """
    hashed_password = bcrypt.generate_password_hash(password).decode("utf-8")
    user = {"username": username, "password": hashed_password, "role": role}
    mongo.db.users.insert_one(user)

