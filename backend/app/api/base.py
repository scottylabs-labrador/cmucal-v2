from flask import Blueprint, jsonify, current_app
from app.services.db import get_db
import os
# from app.config.settings import Config

base_bp = Blueprint("base", __name__)

@base_bp.route("/")
def home():
    # print(Config["JWT_SECRET_KEY"])
    print('hi')
    print('there')
    print('key', os.getenv("JWT_SECRET_KEY"))
    return "Welcome to the CMUCal Flask API!"


@base_bp.route("/test_mongo", methods=["GET"])
def test_mongo():
    """Check if MongoDB is accessible"""
    try:
        db = get_db()
        if db is None:
            print("db is None!")
            return jsonify({"error": "Mongo not initialized"}), 500
        
        collections = db.list_collection_names()

        return jsonify({
            "msg": "MongoDB connection successful",
            "database": "CMUCal",
            "collections": collections
        }), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500