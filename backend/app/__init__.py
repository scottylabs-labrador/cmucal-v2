# Initializes the Flask app, database, and JWT authentication.
from flask import Flask, json
from flask_jwt_extended import JWTManager
from flask_cors import CORS
from app.config.settings import Config
from app.api.auth import auth_bp
from app.api.users import users_bp
from app.api.admin import admin_bp
from app.api.base import base_bp
from app.api.webhook import webhook_bp

from dotenv import load_dotenv
from app.services.db import init_db


# Load environment variables from .env file
load_dotenv()

def create_app():
    app = Flask(__name__)

    # app.json = json.provider.DefaultJSONProvider(app)
    

    # Bind the Flask app to mongo
    init_db(app)

    CORS(app)
    JWTManager(app)

    # Register blueprints (modular routing)
    app.register_blueprint(auth_bp, url_prefix="/api/auth")
    app.register_blueprint(users_bp, url_prefix="/api/users")
    app.register_blueprint(admin_bp, url_prefix="/api/admin")
    app.register_blueprint(webhook_bp, url_prefix="/api/webhook")
    app.register_blueprint(base_bp)

    return app
