from flask import Blueprint, jsonify, current_app

base_bp = Blueprint("base", __name__)

@base_bp.route("/")
def home():
    return "Welcome to the CMUCal Flask API!"

@base_bp.route("/test_mongo", methods=["GET"])
def test_mongo():
    """Check if MongoDB is accessible"""
    try:
        mongo = current_app.extensions["pymongo"]
        db = mongo.db

        if "CMUCal" not in db.client.list_database_names():
            return jsonify({"error": "CMUCal database not found"}), 404
        
        cmucal_db = db.client["CMUCal"]
        collections = cmucal_db.list_collection_names()

        return jsonify({
            "msg": "MongoDB connection successful",
            "database": "CMUCal",
            "collections": collections
        }), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500