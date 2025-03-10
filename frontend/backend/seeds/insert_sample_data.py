from pymongo import MongoClient
import datetime

client = MongoClient("mongodb://localhost:27017/")
db = client.smart_home
energy_collection = db["energy_data"]

sample_data = [
    {"device_id": "device1", "timestamp": datetime.datetime(2024, 2, 1, 10, 30), "energy_consumed": 50},
    {"device_id": "device2", "timestamp": datetime.datetime(2024, 2, 1, 11, 30), "energy_consumed": 75},
    {"device_id": "device3", "timestamp": datetime.datetime(2024, 2, 2, 14, 45), "energy_consumed": 120}
]

energy_collection.insert_many(sample_data)
print("Sample data inserted.")
