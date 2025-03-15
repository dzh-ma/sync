from pymongo import MongoClient
import datetime
import random

# Connect to MongoDB
client = MongoClient("mongodb://localhost:27017/")
db = client.smart_home
energy_collection = db["energy_data"]

# Clear previous data (optional)
energy_collection.delete_many({})

# Sample locations
locations = ["London", "New York", "Berlin", "Paris", "Tokyo", "Dubai", "Sydney"]

# Generate 1000 sample data entries
sample_data = []
start_date = datetime.datetime(2024, 1, 1)
for i in range(1000):
    device_id = f"device_{random.randint(1, 20)}"  # 20 unique devices
    timestamp = start_date + datetime.timedelta(minutes=random.randint(0, 100000))  # Random timestamp within ~70 days
    energy_consumed = round(random.uniform(5.0, 150.0), 2)  # Random energy consumption between 5 and 150 kWh
    location = random.choice(locations)
    
    sample_data.append({
        "device_id": device_id,
        "timestamp": timestamp,
        "energy_consumed": energy_consumed,
        "location": location
    })

# Insert the sample data into the collection
energy_collection.insert_many(sample_data)
print("Inserted 1000 sample energy data entries.")
