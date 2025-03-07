# Stores configuration like database URI, JWT secret key.
import os

class Config:
    SECRET_KEY = os.getenv("SECRET_KEY", "supersecretkey")
    JWT_SECRET_KEY = os.getenv("JWT_SECRET_KEY", "your-jwt-secret")
    MONGO_URI = os.getenv("MONGO_URI", "mongodb://localhost:27017/flaskapp")
    GOOGLE_CLIENT_SECRET_FILE = "client_secret.json"  # Google API credentials
    GOOGLE_SCOPES = ["https://www.googleapis.com/auth/calendar.readonly"]


