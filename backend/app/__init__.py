# Initializes the Flask app, database, and JWT authentication.
from flask import Flask

from flask_cors import CORS
from app.api.users import users_bp
from app.api.base import base_bp
from app.api.google_oauth import google_bp
from app.services.db import SessionLocal, Base


from dotenv import load_dotenv
import os


os.environ["OAUTHLIB_INSECURE_TRANSPORT"] = "1"

# Load environment variables from .env file
load_dotenv()

def create_app():
    app = Flask(__name__)
    app.secret_key = os.getenv("FLASK_SECRET_KEY")

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

    CORS(app, resources={r"/api/*": {"origins": "http://localhost:3000"}}, supports_credentials=True)

    # Bind the Flask app to mongo
    # init_db(app)


    # Register blueprints (modular routing)
    app.register_blueprint(users_bp, url_prefix="/api/users")
    app.register_blueprint(google_bp, url_prefix="/api/google")
    app.register_blueprint(base_bp)

    # CORS(app, resources={r"/api/*": {"origins": "http://localhost:3000"}}, supports_credentials=True, automatic_options=True)
    

    return app