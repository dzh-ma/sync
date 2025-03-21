"""
CLI script to generate energy reports directly from the command line.
"""
import os
import sys
import uuid
import argparse
from datetime import datetime, timedelta

# Add the parent directory to sys.path to ensure modules can be imported
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.db.data import u_c, d_c, us_c, r_c  # Import all collections
from app.models.report import ReportDB, ReportFormat
from app.services.report_service import ReportService

def parse_args():
    """Parse command line arguments."""
    parser = argparse.ArgumentParser(description="Generate energy usage reports")
    
    parser.add_argument("--user_id", required=True, help="User ID to generate report for")
    parser.add_argument("--format", choices=["pdf", "csv"], default="pdf", help="Report format")
    parser.add_argument("--days", type=int, default=30, help="Number of days to include in report")
    parser.add_argument("--title", help="Report title")
    parser.add_argument("--device_ids", nargs="+", help="Specific device IDs to include (space-separated)")
    parser.add_argument("--report_type", default="energy", help="Report type (default: energy)")
    parser.add_argument("--historical", action="store_true", help="Use historical data (March 2024)")
    
    return parser.parse_args()

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

def main():
    """Generate a report based on command line arguments."""
    args = parse_args()
    
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
    mongo_id = ReportService.create_report(report_db)
    print(f"Report record created with MongoDB ID: {mongo_id}")
    print(f"Report UUID: {report_uuid}")
    
    # Generate the report using the UUID we assigned
    print("Generating report...")
    success, file_path, error = ReportService.generate_report(report_uuid)
    
    if success and file_path:
        print(f"Report successfully generated!")
        print(f"Report file: {file_path}")
    else:
        print(f"Error generating report: {error}")

if __name__ == "__main__":
    main()
