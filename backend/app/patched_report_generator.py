"""
Patched version of report generator that handles None values.
"""
import os
import sys
import uuid
import argparse
import traceback
from datetime import datetime, timedelta

# Add the parent directory to sys.path to ensure modules can be imported
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.db.data import u_c, d_c, us_c, r_c
from app.models.report import ReportDB, ReportFormat

def validate_user_id(user_id):
    """Check if the user exists in the database."""
    user = u_c.find_one({"id": user_id})
    if not user:
        print(f"Error: User with ID {user_id} not found.")
        sys.exit(1)
    return user

def get_user_devices(user_id):
    """Get all devices for a user."""
    devices = list(d_c.find({"user_id": user_id}))
    return devices

def fetch_energy_data(user_id, start_date, end_date, device_ids=None):
    """
    Patched version of fetch_energy_data that handles None values.
    """
    # Build the query
    query = {}
    
    # Filter by device IDs
    if device_ids:
        query["device_id"] = {"$in": device_ids}
    else:
        # Get all devices owned by the user
        user_devices = list(d_c.find({"user_id": user_id}))
        if not user_devices:
            return []
        
        user_device_ids = [device["id"] for device in user_devices]
        if user_device_ids:
            query["device_id"] = {"$in": user_device_ids}
        else:
            return []
    
    # Add date range filter
    if start_date or end_date:
        timestamp_query = {}
        if start_date:
            timestamp_query["$gte"] = start_date
        if end_date:
            timestamp_query["$lte"] = end_date
            
        if timestamp_query:
            query["timestamp"] = timestamp_query
    
    # Execute the query
    print(f"Query: {query}")
    cursor = us_c.find(query).sort("timestamp", 1)
    print(f"Cursor type: {type(cursor)}")
    usage_data = list(cursor)
    print(f"Usage data type: {type(usage_data)}, length: {len(usage_data)}")
    
    # Fix missing or None values
    for i, record in enumerate(usage_data):
        # Fill in missing energy_consumed with zeros
        if "energy_consumed" not in record or record["energy_consumed"] is None:
            print(f"Fixing record {i}: Adding default energy_consumed = 0.0")
            record["energy_consumed"] = 0.0
        
        # Convert timestamp to ISO format if it's a datetime object
        if "timestamp" in record and isinstance(record["timestamp"], datetime):
            record["timestamp"] = record["timestamp"].isoformat()
    
    # Enhance usage data with device information
    enhanced_data = []
    for record in usage_data:
        # Get device info
        device_id = record.get("device_id")
        device = d_c.find_one({"id": device_id})
        
        # Create enhanced record with location
        enhanced_record = {
            "timestamp": record.get("timestamp"),
            "device_id": device_id,
            "energy_consumed": record.get("energy_consumed", 0.0),  # Default to 0 if missing
            "location": device.get("room_id") if device else "Unknown"
        }
        
        enhanced_data.append(enhanced_record)
    
    return enhanced_data

def fetch_user_data(user_id):
    """Fetch user data for report personalization."""
    user = u_c.find_one({"id": user_id})
    
    if not user:
        return {}
    
    return {
        "email": user.get("email"),
        "username": user.get("username")
    }

def generate_energy_report(energy_data, user_data=None, format="pdf", start_date=None, end_date=None):
    """
    Patched version that handles the path to the report generator.
    """
    from app.utils.report.report_generator import generate_energy_report as gen_report
    
    # Print some debug info
    print(f"Generating {format} report with {len(energy_data)} records")
    if len(energy_data) > 0:
        sample = energy_data[0]
        print(f"Sample record: {sample}")
    
    # Call the original function
    try:
        report_path = gen_report(
            energy_data=energy_data,
            user_data=user_data,
            format=format.lower(),
            start_date=start_date,
            end_date=end_date
        )
        return report_path
    except Exception as e:
        traceback.print_exc()
        print(f"Error in report generation: {e}")
        return None

def generate_report(report_id):
    """
    Patched version of generate_report that uses our fixed functions.
    """
    # Get report data
    report_data = r_c.find_one({"id": report_id})
    if not report_data:
        return False, None, "Report not found"
    
    try:
        # Update status to generating
        r_c.update_one(
            {"id": report_id},
            {"$set": {"status": "generating", "updated": datetime.utcnow()}}
        )
        
        # Fetch energy data with our patched function
        start_date = None
        end_date = None
        
        if report_data.get("start_date"):
            start_date = datetime.strptime(report_data["start_date"], "%Y-%m-%d")
        if report_data.get("end_date"):
            end_date = datetime.strptime(report_data["end_date"], "%Y-%m-%d") + timedelta(days=1) - timedelta(seconds=1)
        
        energy_data = fetch_energy_data(
            user_id=report_data["user_id"],
            start_date=start_date,
            end_date=end_date,
            device_ids=report_data.get("device_ids")
        )
        
        if not energy_data:
            error_msg = "No energy data found for the specified criteria"
            r_c.update_one(
                {"id": report_id},
                {"$set": {"status": "failed", "error_message": error_msg, "updated": datetime.utcnow()}}
            )
            return False, None, error_msg
        
        # Fetch user data for personalization
        user_data = fetch_user_data(report_data["user_id"])
        
        # Generate the report with our patched function
        report_path = generate_energy_report(
            energy_data=energy_data,
            user_data=user_data,
            format=report_data["format"].lower(),
            start_date=report_data.get("start_date"),
            end_date=report_data.get("end_date")
        )
        
        if not report_path:
            error_msg = "Failed to generate report file"
            r_c.update_one(
                {"id": report_id},
                {"$set": {"status": "failed", "error_message": error_msg, "updated": datetime.utcnow()}}
            )
            return False, None, error_msg
        
        # Update the report record with success status
        r_c.update_one(
            {"id": report_id},
            {"$set": {
                "status": "completed",
                "file_path": report_path,
                "completed": datetime.utcnow(),
                "updated": datetime.utcnow()
            }}
        )
        
        return True, report_path, None
            
    except Exception as e:
        # Update the report record with failure status
        error_message = str(e)
        r_c.update_one(
            {"id": report_id},
            {"$set": {"status": "failed", "error_message": error_message, "updated": datetime.utcnow()}}
        )
        
        return False, None, error_message

def main():
    """Patched report generation script."""
    parser = argparse.ArgumentParser(description="Generate energy usage reports")
    
    parser.add_argument("--user_id", required=True, help="User ID to generate report for")
    parser.add_argument("--format", choices=["pdf", "csv"], default="pdf", help="Report format")
    parser.add_argument("--days", type=int, default=30, help="Number of days to include in report")
    parser.add_argument("--title", help="Report title")
    parser.add_argument("--device_ids", nargs="+", help="Specific device IDs to include (space-separated)")
    parser.add_argument("--report_type", default="energy", help="Report type (default: energy)")
    parser.add_argument("--historical", action="store_true", help="Use historical data (March 2024)")
    
    args = parse_args = parser.parse_args()
    
    # Validate user
    user = validate_user_id(args.user_id)
    print(f"Generating report for user: {user.get('username', user.get('email', 'Unknown'))}")
    
    # Determine date range
    if args.historical:
        # Use March 2024 dates where we know data exists
        end_date = datetime(2024, 3, 19)  # Latest record date
        start_date = end_date - timedelta(days=args.days)
        print("Using historical data period (March 2024)")
    else:
        # Use current dates
        end_date = datetime.now()
        start_date = end_date - timedelta(days=args.days)
        print("Using current date period")
    
    start_date_str = start_date.strftime("%Y-%m-%d")
    end_date_str = end_date.strftime("%Y-%m-%d")
    print(f"Date range: {start_date_str} to {end_date_str}")
    
    # Get device IDs if not specified
    device_ids = args.device_ids
    if not device_ids:
        devices = get_user_devices(args.user_id)
        device_ids = [device["id"] for device in devices]
        print(f"Using all devices ({len(device_ids)}) for the user")
    else:
        print(f"Using specified devices: {', '.join(device_ids)}")
    
    # Create a title if not specified
    title = args.title
    if not title:
        title = f"Energy Report ({start_date_str} to {end_date_str})"
    
    # Generate a UUID for the report
    report_uuid = str(uuid.uuid4())
    
    # Create report object
    report_db = ReportDB(
        id=report_uuid,
        user_id=args.user_id,
        title=title,
        format=args.format.lower(),
        report_type=args.report_type,
        start_date=start_date_str,
        end_date=end_date_str,
        device_ids=device_ids,
        status="pending"
    )
    
    # Create report in database
    print("Creating report record...")
    result = r_c.insert_one(report_db.model_dump())
    print(f"Report record created with MongoDB ID: {result.inserted_id}")
    print(f"Report UUID: {report_uuid}")
    
    # Generate the report using the UUID we assigned
    print("Generating report...")
    success, file_path, error = generate_report(report_uuid)
    
    if success and file_path:
        print(f"Report successfully generated!")
        print(f"Report file: {file_path}")
    else:
        print(f"Error generating report: {error}")

if __name__ == "__main__":
    main()
