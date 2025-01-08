from pymongo import MongoClient

client = MongoClient("mongodb://localhost:27017/")
db = client["project_database"]
users_collection = db["users"]

def init_db():
    # Any necessary setup tasks (like creating indexes)
    users_collection.create_index("email", unique=True)
