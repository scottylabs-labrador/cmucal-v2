from flask_pymongo import PyMongo
from flask import Flask
from app.config.settings import Config

mongo = PyMongo()

def init_db(app: Flask):
    # print("Using MONGO_URI:", Config.MONGO_URI)
    # app.config["MONGO_URI"] = Config.MONGO_URI
    mongo.init_app(app)
    