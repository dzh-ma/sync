from pymongo import MongoClient

client = MongoClient("mongodb://localhost:27017/")
# db = client["project_database"]
db = client.smart_home
users_collection = db["users"]

async def init_db():
    # Any necessary setup tasks (like creating indexes)
    users_collection.create_index("email", unique = True)
