# Initializes the Flask app, database, and JWT authentication.
from flask import Flask, json
# from flask_jwt_extended import JWTManager
from flask_cors import CORS
# from app.config.settings import Config
# from app.api.auth import auth_bp
from app.api.users import users_bp
# from app.api.admin import admin_bp
from app.api.base import base_bp
from app.api.webhook import webhook_bp
from app.api.google_oauth import google_bp

from dotenv import load_dotenv
from app.services.db import init_db
import os

os.environ["OAUTHLIB_INSECURE_TRANSPORT"] = "1"

# Load environment variables from .env file
load_dotenv()

def create_app():
    app = Flask(__name__)

    # app.json = json.provider.DefaultJSONProvider(app)
    app.config["SECRET_KEY"] = os.getenv("SECRET_KEY")
    app.config["JWT_SECRET_KEY"] = os.getenv("JWT_SECRET_KEY")
    app.config["MONGO_URI"] = os.getenv("MONGO_URI")
    # app.config["NEXT_PUBLIC_GOOGLE_CLIENT_ID"] = os.getenv("NEXT_PUBLIC_GOOGLE_CLIENT_ID")
    # app.config["GOOGLE_CLIENT_SECRET_FILE"] = "client_secret.json"
    app.config["GOOGLE_CLIENT_ID"] = os.getenv("GOOGLE_CLIENT_ID")
    app.config["GOOGLE_CLIENT_SECRET"] = os.getenv("GOOGLE_CLIENT_SECRET")
    app.config["GOOGLE_REDIRECT_URI"] = os.getenv("GOOGLE_REDIRECT_URI")
    app.config["FRONTEND_REDIRECT_URI"] = os.getenv("FRONTEND_REDIRECT_URI")
    

    # Bind the Flask app to mongo
    init_db(app)

    CORS(app)
    CORS(google_bp, supports_credentials=True)

    # JWTManager(app)

    # Register blueprints (modular routing)
    # app.register_blueprint(auth_bp, url_prefix="/api/auth")
    app.register_blueprint(users_bp, url_prefix="/api/users")
    # app.register_blueprint(admin_bp, url_prefix="/api/admin")
    app.register_blueprint(webhook_bp, url_prefix="/api/webhook")
    app.register_blueprint(google_bp, url_prefix="/api/google")
    app.register_blueprint(base_bp)

    return app
