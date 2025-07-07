from flask import Blueprint, request, jsonify
# from app.services.db import get_db
# import os
# from app.config.settings import Config
from app.services.db import Base, SessionLocal
from sqlalchemy import text
from app.models.models import User 


base_bp = Blueprint("base", __name__)

@base_bp.route("/")
def home():
    print('hi')
    print('there')
    return "Welcome to the CMUCal Flask API!"


@base_bp.route("/test_db", methods=["GET"])
def db_health_check():
    with SessionLocal() as db:
        try:
            user = User(clerk_id="123456")
            db.add(user)
            db.commit()
            db.refresh(user)
            return jsonify({"status": "connected"})
        except Exception as e:
            return jsonify({"status": "error", "details": str(e)}), 500
