from pymongo import MongoClient

# Replace with your actual MongoDB URI

try:
    client = MongoClient(MONGO_URI)
    db = client["CMUCal"]  # Replace with your actual database name

    # Test connection
    print("MongoDB server info:", client.server_info())  # Should print MongoDB details
    print("Databases:", db.list_collection_names())  # Should list databases
    db["users"].insert_one({"clerk_id": "test_123", "role": "user"})

except Exception as e:
    print("Failed to connect to MongoDB:", e)
