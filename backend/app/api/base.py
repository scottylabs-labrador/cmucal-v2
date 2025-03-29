from flask import Blueprint, jsonify, current_app
from app.services.db import mongo

base_bp = Blueprint("base", __name__)

@base_bp.route("/")
def home():
    return "Welcome to the CMUCal Flask API!"


@base_bp.route("/ping_mongo")
def ping_mongo():
    try:
        client = mongo.cx  # Short for `mongo._get_client()`
        return jsonify({"databases": client.list_database_names()})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

# need to test mongo connection
@base_bp.route("/test_mongo", methods=["GET"])
def test_mongo():
    """Check if MongoDB is accessible"""
    try:
        db = mongo.cx["CMUCal"]
        if db is None:
            return jsonify({"error": "Mongo not initialized"}), 500
        
        collections = db.list_collection_names()

        return jsonify({
            "msg": "MongoDB connection successful",
            "database": "CMUCal",
            "collections": collections
        }), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500