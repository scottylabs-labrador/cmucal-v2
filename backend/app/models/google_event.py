# # handles DB logic
# from pymongo import MongoClient
# from datetime import datetime, timezone
# from app.services.db import get_db 

# def save_google_event(user_id, local_event_id, google_event_id, title, start, end):
#     db = get_db()
#     db.synced_events.insert_one({
#         "user_id": user_id,
#         "local_event_id": local_event_id,
#         "google_event_id": google_event_id,
#         "title": title,
#         "start": start,
#         "end": end,
#         "synced_at": datetime.now(timezone.utc)
#     })

# def get_google_event_by_local_id(user_id, local_event_id):
#     db = get_db()
#     return db.synced_events.find_one({
#         "user_id": user_id,
#         "local_event_id": local_event_id
#     })

# def delete_google_event_by_local_id(user_id, local_event_id):
#     db = get_db()
#     return db.synced_events.delete_one({
#         "user_id": user_id,
#         "local_event_id": local_event_id
#     })
