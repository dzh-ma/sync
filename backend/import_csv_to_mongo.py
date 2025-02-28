import csv
from pymongo import MongoClient

# Connect to MongoDB
client = MongoClient('mongodb://localhost:27017/')
db = client['project_test']  # Use the project_test database
devices_collection = db['devices']

# Import CSV data
def import_csv_to_mongo(csv_file_path):
    with open(csv_file_path, newline='') as csvfile:
        reader = csv.DictReader(csvfile)
        for row in reader:
            devices_collection.insert_one({
                'name': row['Device Name'],
                'category': row['Category'],
                'type': row['Type'],
                'energy_usage_per_hour': float(row['Estimated Energy Usage per Hour (kW)'])
            })

# Call the function with the path to your CSV file
import_csv_to_mongo('iot_devices_dataset_realistic.csv') 