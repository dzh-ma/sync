"""
CLI tool for generating energy usage reports.
"""
import os
import sys
import uuid
import argparse
from datetime import datetime, timedelta
import asyncio
from motor.motor_asyncio import AsyncIOMotorClient
from bson import ObjectId

# Database connection
MONGO_URI = os.getenv("MONGO_URI", "mongodb://localhost:27017")
client = AsyncIOMotorClient(MONGO_URI)
db = client.project_test

# Collections
admin_users_collection = db['admin_users']
user_devices_collection = db['user_devices']
household_members_collection = db['household_members']
statistics_collection = db['statistics']
reports_collection = db['reports']

# Create reports directory if it doesn't exist
REPORTS_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "generated_reports")
os.makedirs(REPORTS_DIR, exist_ok=True)

def parse_args():
    """Parse command-line arguments for report generation."""
    parser = argparse.ArgumentParser(description="Generate energy usage reports")
    
    parser.add_argument("--user-id", required=True, help="User ID to generate report for")
    parser.add_argument("--format", choices=["pdf", "csv"], default="pdf", help="Report format")
    parser.add_argument("--days", type=int, default=30, help="Number of days to include in report")
    parser.add_argument("--title", help="Report title")
    parser.add_argument("--device-ids", nargs="+", help="Specific device IDs to include (space-separated)")
    parser.add_argument("--household-id", help="Household ID (if different from user's default)")
    
    return parser.parse_args()

async def validate_user_id(user_id):
    """Verify the user ID exists in the database."""
    # Check if it's an ObjectId (admin user)
    if ObjectId.is_valid(user_id):
        user = await admin_users_collection.find_one({"_id": ObjectId(user_id)})
        if user:
            print(f"Found admin user: {user.get('admin_email')}")
            return user
    
    # Check if it's an email (household member)
    member = await household_members_collection.find_one({"email": user_id})
    if member:
        print(f"Found household member: {member.get('name')}")
        return member
    
    print(f"Error: User with ID '{user_id}' not found")
    return None

async def get_user_devices(user_id, household_id=None):
    """Get all devices for a user."""
    query = {"user_id": user_id}
    if household_id:
        query["household_id"] = household_id
        
    devices = await user_devices_collection.find(query).to_list(length=100)
    return devices

# Import the same generate_energy_report function from your main app
from main import generate_energy_report

async def create_and_generate_report(user_id, title, format, start_date, end_date, device_ids, household_id=None):
    """Create a report record and generate the report file."""
    # Create a report ID
    report_id = str(uuid.uuid4())
    
    # Get user data
    user_data = {}
    if ObjectId.is_valid(user_id):
        admin_user = await admin_users_collection.find_one({"_id": ObjectId(user_id)})
        if admin_user:
            user_data = {
                "email": admin_user.get("admin_email"),
                "username": f"{admin_user.get('firstName', '')} {admin_user.get('lastName', '')}"
            }
            # Use the user's household ID if none specified
            if not household_id and admin_user.get("household_id"):
                household_id = admin_user.get("household_id")
    else:
        # Check if it's a household member
        member = await household_members_collection.find_one({"email": user_id})
        if member:
            user_data = {
                "email": member.get("email"),
                "username": member.get("name")
            }
            # Use the member's household ID if none specified
            if not household_id and member.get("household_id"):
                household_id = member.get("household_id")
    
    print(f"Creating report: {title}, Format: {format}")
    print(f"Date range: {start_date} to {end_date}")
    
    # Create the report record
    now = datetime.utcnow()
    report = {
        "id": report_id,
        "user_id": user_id,
        "household_id": household_id,
        "title": title,
        "format": format,
        "start_date": start_date,
        "end_date": end_date,
        "device_ids": device_ids or [],
        "status": "pending",
        "created": now,
        "updated": now
    }
    
    # Insert the report into the database
    await reports_collection.insert_one(report)
    print(f"Created report record with ID: {report_id}")
    
    try:
        # Update status to generating
        await reports_collection.update_one(
            {"id": report_id},
            {"$set": {"status": "generating", "updated": datetime.utcnow()}}
        )
        
        # Convert string dates to datetime
        start_datetime = datetime.strptime(start_date, "%Y-%m-%d") if start_date else None
        end_datetime = datetime.strptime(end_date, "%Y-%m-%d") + timedelta(days=1) - timedelta(seconds=1) if end_date else None
        
        # Build query for statistics
        query = {}
        if household_id:
            query["household_id"] = household_id
        else:
            query["user_id"] = user_id
            
        # Add date filter
        if start_datetime or end_datetime:
            date_filter = {}
            if start_datetime:
                date_filter["$gte"] = start_datetime
            if end_datetime:
                date_filter["$lte"] = end_datetime
            
            if date_filter:
                query["timestamp"] = date_filter
        
        # Filter by devices if specified
        if device_ids:
            query["$or"] = [
                {"device_types.type": {"$in": device_ids}},
                {"devices": {"$in": device_ids}}
            ]
        
        print(f"Query: {query}")
        
        # Fetch energy data
        records = await statistics_collection.find(query).sort("timestamp", 1).to_list(length=1000)
        print(f"Found {len(records)} statistics records")
        
        if not records:
            print("No energy data found - report generation failed")
            await reports_collection.update_one(
                {"id": report_id},
                {
                    "$set": {
                        "status": "failed", 
                        "error_message": "No energy data found for the specified criteria",
                        "updated": datetime.utcnow()
                    }
                }
            )
            return False, "No energy data found"
        
        # Process records for the report generator
        energy_data = []
        for record in records:
            # Process device types
            if "device_types" in record:
                for device_type in record["device_types"]:
                    energy_data.append({
                        "timestamp": record.get("timestamp"),
                        "device_id": device_type["type"],
                        "energy_consumed": device_type["energy"],
                        "location": "Unknown"  # Default location
                    })
            # Add basic record if no device types
            else:
                energy_data.append({
                    "timestamp": record.get("timestamp"),
                    "device_id": "Unknown",
                    "energy_consumed": record.get("total_energy", 0),
                    "location": "Unknown"
                })
        
        # Generate the report file
        report_path = generate_energy_report(
            energy_data=energy_data,
            user_data=user_data,
            format=format.lower(),
            start_date=start_date,
            end_date=end_date
        )
        
        if not report_path:
            print("Failed to generate report file")
            await reports_collection.update_one(
                {"id": report_id},
                {
                    "$set": {
                        "status": "failed", 
                        "error_message": "Failed to generate report file",
                        "updated": datetime.utcnow()
                    }
                }
            )
            return False, "Failed to generate report file"
        
        # Update report with success status
        await reports_collection.update_one(
            {"id": report_id},
            {
                "$set": {
                    "status": "completed",
                    "file_path": report_path,
                    "completed": datetime.utcnow(),
                    "updated": datetime.utcnow()
                }
            }
        )
        
        print(f"Report generated successfully: {report_path}")
        return True, report_path
        
    except Exception as e:
        print(f"Error generating report: {str(e)}")
        await reports_collection.update_one(
            {"id": report_id},
            {
                "$set": {
                    "status": "failed",
                    "error_message": str(e),
                    "updated": datetime.utcnow()
                }
            }
        )
        return False, str(e)

async def main():
    """Main CLI function."""
    args = parse_args()
    
    # Validate user ID
    user = await validate_user_id(args.user_id)
    if not user:
        sys.exit(1)
    
    # Determine date range
    end_date = datetime.now().date()
    start_date = end_date - timedelta(days=args.days)
    
    # Format dates for the report
    start_date_str = start_date.strftime("%Y-%m-%d")
    end_date_str = end_date.strftime("%Y-%m-%d")
    
    # Create a default title if not provided
    title = args.title or f"Energy Report ({start_date_str} to {end_date_str})"
    
    # Generate the report
    success, result = await create_and_generate_report(
        user_id=args.user_id,
        title=title,
        format=args.format,
        start_date=start_date_str,
        end_date=end_date_str,
        device_ids=args.device_ids,
        household_id=args.household_id
    )
    
    if success:
        print(f"Successfully generated report: {result}")
        sys.exit(0)
    else:
        print(f"Failed to generate report: {result}")
        sys.exit(1)

if __name__ == "__main__":
    asyncio.run(main())
