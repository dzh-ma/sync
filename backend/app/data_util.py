"""
Utility to check for usage data and optionally generate test data.
"""
import os
import sys
import uuid
import random
from datetime import datetime, timedelta

# Add the parent directory to sys.path to ensure modules can be imported
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.db.data import us_c, d_c

def check_usage_data(user_id, days=30):
    """Check if usage data exists for a user's devices."""
    # Get devices for the user
    devices = list(d_c.find({"user_id": user_id}))
    device_ids = [device["id"] for device in devices]
    
    if not device_ids:
        print(f"No devices found for user {user_id}")
        return False
    
    print(f"Found {len(device_ids)} devices for user {user_id}")
    
    # Check for usage data within the specified time range
    end_date = datetime.now()
    start_date = end_date - timedelta(days=days)
    
    query = {
        "device_id": {"$in": device_ids},
        "timestamp": {
            "$gte": start_date,
            "$lte": end_date
        }
    }
    
    count = us_c.count_documents(query)
    
    if count > 0:
        print(f"Found {count} usage records in the last {days} days")
        return True
    else:
        print(f"No usage records found in the last {days} days")
        # Check if there's any usage data at all for these devices
        all_time_count = us_c.count_documents({"device_id": {"$in": device_ids}})
        if all_time_count > 0:
            print(f"Found {all_time_count} usage records for these devices across all time")
            # Show the earliest and latest records
            earliest = us_c.find({"device_id": {"$in": device_ids}}).sort("timestamp", 1).limit(1)
            latest = us_c.find({"device_id": {"$in": device_ids}}).sort("timestamp", -1).limit(1)
            
            earliest_list = list(earliest)
            latest_list = list(latest)
            
            if earliest_list:
                print(f"Earliest record: {earliest_list[0].get('timestamp')}")
            if latest_list:
                print(f"Latest record: {latest_list[0].get('timestamp')}")
        else:
            print("No usage records found for these devices at all")
        return False

def generate_test_data(user_id, days=30, records_per_device=5):
    """Generate test usage data for a user's devices."""
    # Get devices for the user
    devices = list(d_c.find({"user_id": user_id}))
    
    if not devices:
        print(f"No devices found for user {user_id}")
        return False
    
    print(f"Generating test data for {len(devices)} devices")
    
    # Generate data
    end_date = datetime.now()
    start_date = end_date - timedelta(days=days)
    
    generated_count = 0
    
    for device in devices:
        device_id = device["id"]
        device_name = device.get("name", "Unknown Device")
        
        for _ in range(records_per_device):
            # Generate a random timestamp in the date range
            random_days = random.randint(0, days)
            timestamp = end_date - timedelta(days=random_days)
            
            # Generate random energy consumption (0.1 to 5.0 kWh)
            energy_consumed = round(random.uniform(0.1, 5.0), 2)
            
            # Generate random duration (10 to 480 minutes)
            duration = random.randint(10, 480)
            
            # Create usage record
            usage_record = {
                "id": str(uuid.uuid4()),
                "device_id": device_id,
                "timestamp": timestamp,
                "energy_consumed": energy_consumed,
                "duration": duration,
                "status": random.choice(["active", "idle"]),
                "metrics": {
                    "temperature": round(random.uniform(18, 28), 1) if random.random() > 0.5 else None,
                    "brightness": random.randint(10, 100) if "light" in device_name.lower() else None,
                    "usage_minutes": duration
                },
                "created": timestamp
            }
            
            # Insert into the database
            us_c.insert_one(usage_record)
            generated_count += 1
    
    print(f"Generated {generated_count} test usage records")
    return True

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python data_util.py <user_id> [--generate] [--days N] [--records N]")
        sys.exit(1)
    
    user_id = sys.argv[1]
    
    # Parse options
    generate = "--generate" in sys.argv
    
    # Check for --days option
    days = 30  # Default
    if "--days" in sys.argv:
        try:
            days_index = sys.argv.index("--days") + 1
            days = int(sys.argv[days_index])
        except (IndexError, ValueError):
            print("Invalid days value. Using default of 30.")
    
    # Check for --records option (records per device)
    records_per_device = 5  # Default
    if "--records" in sys.argv:
        try:
            records_index = sys.argv.index("--records") + 1
            records_per_device = int(sys.argv[records_index])
        except (IndexError, ValueError):
            print("Invalid records value. Using default of 5.")
    
    # Check for existing data
    has_data = check_usage_data(user_id, days)
    
    # Generate test data if requested
    if generate:
        generate_test_data(user_id, days, records_per_device)
        # Verify data was generated
        check_usage_data(user_id, days)
