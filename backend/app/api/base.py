from flask import Blueprint, jsonify, current_app

base_bp = Blueprint("base", __name__)

@base_bp.route("/")
def home():
    return "Welcome to the CMUCal Flask API!"
