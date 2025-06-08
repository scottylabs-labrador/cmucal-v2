# app/services/db.py
import os
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base
from dotenv import load_dotenv

load_dotenv()

DATABASE_URL = os.getenv("SUPABASE_DB_URL")
print("Using DATABASE_URL:", DATABASE_URL)

# Create SQLAlchemy engine
engine = create_engine(DATABASE_URL, echo=True)

# Session maker for DB sessions
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Base class for models
Base = declarative_base()
