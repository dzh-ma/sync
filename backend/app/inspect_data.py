"""
Script to inspect and fix usage data for generating reports.
"""
import os
import sys
from datetime import datetime

# Add the parent directory to sys.path to ensure modules can be imported
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.db.data import us_c, d_c

def inspect_usage_data(user_id, start_date, end_date):
    """Inspect usage data for a user in a specific date range."""
    # Get devices for the user
    devices = list(d_c.find({"user_id": user_id}))
    device_ids = [device["id"] for device in devices]
    
    if not device_ids:
        print(f"No devices found for user {user_id}")
        return
    
    # Build query
    query = {
        "device_id": {"$in": device_ids},
        "timestamp": {
            "$gte": start_date,
            "$lte": end_date
        }
    }
    
    # Fetch the records
    records = list(us_c.find(query))
    print(f"Found {len(records)} records in the date range")
    
    # Check for missing fields
    fields_to_check = ["energy_consumed", "duration", "status", "metrics"]
    missing_data = {}
    
    for field in fields_to_check:
        missing_data[field] = 0
    
    for record in records:
        for field in fields_to_check:
            if field not in record or record[field] is None:
                missing_data[field] += 1
                
    print("\nMissing fields summary:")
    for field, count in missing_data.items():
        if count > 0:
            print(f"- {field}: Missing in {count} records ({count/len(records)*100:.1f}%)")
    
    # Show a few example records
    if records:
        print("\nSample record structure:")
        for key, value in records[0].items():
            print(f"- {key}: {type(value).__name__} = {value}")
    
    # Check for None values in energy_consumed
    none_energy = [r for r in records if "energy_consumed" not in r or r["energy_consumed"] is None]
    if none_energy:
        print(f"\nFound {len(none_energy)} records with None energy_consumed values")
        print("Would you like to fix these records? (y/n)")
        response = input().strip().lower()
        
        if response == 'y':
            for record in none_energy:
                # Update with default value
                us_c.update_one(
                    {"_id": record["_id"]},
                    {"$set": {"energy_consumed": 0.0}}
                )
            print(f"Fixed {len(none_energy)} records")
    
    # Return the records for additional processing
    return records

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python inspect_data.py <user_id>")
        sys.exit(1)
    
    user_id = sys.argv[1]
    
    # Use March 2024 date range where we know data exists
    end_date = datetime(2024, 3, 19)
    start_date = datetime(2024, 3, 12)
    
    print(f"Inspecting data for user {user_id}")
    print(f"Date range: {start_date.strftime('%Y-%m-%d')} to {end_date.strftime('%Y-%m-%d')}")
    
    inspect_usage_data(user_id, start_date, end_date)
