# Initializes the Flask app, database, and JWT authentication.
import os
from dotenv import load_dotenv

# Load environment variables from .env file BEFORE other imports
load_dotenv()

from flask import Flask
from flask_cors import CORS
from app.api.users import users_bp
from app.api.organizations import orgs_bp
from app.api.base import base_bp
from app.api.google_oauth import google_bp
from app.api.events import events_bp
from app.api.schedule import schedule_bp
from app.services.db import SessionLocal, Base
from app.cli import import_courses_command


os.environ["OAUTHLIB_INSECURE_TRANSPORT"] = "1"

def create_app():
    app = Flask(__name__)

    app.config["SECRET_KEY"] = os.getenv("SECRET_KEY")
    app.config["JWT_SECRET_KEY"] = os.getenv("JWT_SECRET_KEY")
    app.config["GOOGLE_CLIENT_ID"] = os.getenv("GOOGLE_CLIENT_ID")
    app.config["GOOGLE_CLIENT_SECRET"] = os.getenv("GOOGLE_CLIENT_SECRET")
    app.config["GOOGLE_REDIRECT_URI"] = os.getenv("GOOGLE_REDIRECT_URI")
    app.config["FRONTEND_REDIRECT_URI"] = os.getenv("FRONTEND_REDIRECT_URI")
    
    app.config["SECRET_KEY"] = os.getenv("SECRET_KEY")
    app.config["JWT_SECRET_KEY"] = os.getenv("JWT_SECRET_KEY")
    app.config["MONGO_URI"] = os.getenv("MONGO_URI")
    app.config["GOOGLE_CLIENT_SECRET_FILE"] = "client_secret.json" 

    app.config["SUPABASE_URL"] = os.getenv("SUPABASE_URL")
    app.config["SUPABASE_API_KEY"] = os.getenv("SUPABASE_API_KEY")
    app.config["SUPABASE_DB_URL"] = os.getenv("SUPABASE_DB_URL")

    CORS(app, resources={r"/api/*": {
        "origins": "http://localhost:3000",
        "methods": ["GET", "POST", "PUT", "DELETE", "OPTIONS"],
        "allow_headers": ["Content-Type", "Authorization", "Clerk-User-Id"],
    }}, supports_credentials=True)


    # Register blueprints (modular routing)
    app.register_blueprint(users_bp, url_prefix="/api/users")
    app.register_blueprint(orgs_bp, url_prefix="/api/organizations")
    app.register_blueprint(google_bp, url_prefix="/api/google")
    app.register_blueprint(events_bp, url_prefix="/api/events")
    app.register_blueprint(schedule_bp, url_prefix="/api/schedule")
    app.register_blueprint(base_bp)

    # CORS(app, resources={r"/api/*": {"origins": "http://localhost:3000"}}, supports_credentials=True, automatic_options=True)
    
    # Register CLI command
    app.cli.add_command(import_courses_command)

    return app