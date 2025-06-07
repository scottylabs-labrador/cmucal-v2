from flask import current_app
# app/models/user.py
from sqlalchemy import Column, String, DateTime, BigInteger
from datetime import datetime
from app.services.db import Base, SessionLocal
from flask import request, jsonify

class User(Base):
    __tablename__ = "users"

    id = Column(BigInteger, primary_key=True, autoincrement=True)
    clerk_id = Column(String, nullable=True)
    email = Column(String, nullable=True)
    fname = Column(String, nullable=True)
    lname = Column(String, nullable=True)
    calendar_id = Column(String, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)

def user_to_dict(user):
    return {
        "id": user.id,
        "clerk_id": user.clerk_id,
        "email": user.email,
        "fname": user.fname,
        "lname": user.lname,
        "calendar_id": user.calendar_id,
        "created_at": user.created_at.isoformat() if user.created_at else None,
    }

def create_user(db, clerk_id, **kwargs):
    # db = SessionLocal()
    # user = db.query(User).filter(User.clerk_id == clerk_id).first()
    # if not user:
    user = User(clerk_id=clerk_id, **kwargs)
    db.add(user)
    db.commit()
    db.refresh(user)
    return user

def get_user_by_clerk_id(db, clerk_id):
    return db.query(User).filter(User.clerk_id == clerk_id).first()
    # user = db.query(User).filter(User.clerk_id == clerk_id).first()
    # if user:
    #     return jsonify({
    #         "id": str(user.id),
    #         "email": user.email,
    #         "first_name": user.first_name,
    #         "last_name": user.last_name
    #     })
    # else:
    #     return jsonify({"error": "User not found"}), 404


def update_user_calendar_id(db, clerk_id, calendar_id):
    user = db.query(User).filter(User.clerk_id == clerk_id).first()
    if not user:
        raise ValueError(f"No user found with clerk_id {clerk_id}")

    user.calendar_id = calendar_id
    db.commit()
    db.refresh(user)
    return user

# def get_user_by_clerk_id(clerk_id: str):
#     db = get_db()
#     users_collection = db["users"]
#     return users_collection.find_one({"clerk_id": clerk_id})

# def create_user(clerk_id: str, email: str, first_name: str = "", last_name: str = ""):
#     db = get_db()
#     users_collection = db["users"]
    
#     user_data = {
#         "clerk_id": clerk_id,
#         "email": email,
#         "first_name": first_name,
#         "last_name": last_name,
#     }
    
#     users_collection.insert_one(user_data)
#     return user_data
