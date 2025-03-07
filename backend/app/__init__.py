# Initializes the Flask app, database, and JWT authentication.
from flask import Flask
from flask_jwt_extended import JWTManager
from flask_cors import CORS
from app.config.settings import Config
from app.api.auth import auth_bp
from app.api.users import users_bp
from app.api.admin import admin_bp

def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)

    CORS(app)
    JWTManager(app)

    # Register blueprints (modular routing)
    app.register_blueprint(auth_bp, url_prefix="/api/auth")
    app.register_blueprint(users_bp, url_prefix="/api/users")
    app.register_blueprint(admin_bp, url_prefix="/api/admin")

    return app
