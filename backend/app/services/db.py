from flask_pymongo import PyMongo
from flask import Flask

mongo = PyMongo()
_db = None

def init_db(app: Flask):
    global _db
    mongo.init_app(app)
    _db = mongo.cx["CMUCal"]

def get_db():
    if _db is None:
        raise RuntimeError("Database not initialized. Call init_db(app) first.")
    return _db