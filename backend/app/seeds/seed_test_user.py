"""
Database seeding script for Smart Home Automation platform.
This script creates a single user with admin privileges.
"""
import os
import sys
import uuid
import random
import datetime
import hashlib
from datetime import datetime, timedelta
from passlib.context import CryptContext

pc = CryptContext(schemes=["bcrypt"], deprecated="auto")

# Try to import pymongo, install if not available
try:
    from pymongo import MongoClient
except ImportError:
    print("Installing required packages...")
    os.system("pip install pymongo")
    from pymongo import MongoClient

# Connect to MongoDB
MONGO_URI = os.getenv("MONGO_URI", "mongodb://localhost:27017/")
try:
    client = MongoClient(MONGO_URI)
    db = client.sync

    # Get collections
    user_collection = db["user"]
    profile_collection = db["profile"]

    print(f"Connected to MongoDB database: {MONGO_URI}")
except Exception as e:
    sys.exit(f"Failed to connect to MongoDB: {e}")

# Helper functions
def generate_uuid() -> str:
    """Generate a UUID string."""
    return str(uuid.uuid4())

def hash_password(password: str) -> str:
    """Create a hashed password."""
    # return hashlib.sha256(password.encode()).hexdigest()
    return pc.hash(password)

# Create single admin user
def create_admin_user():
    """Create a single admin user with known credentials."""
    # Define user details
    email = "dzhma@proton.me"
    first_name = "Matin"
    last_name = "Dzhumanov"
    username = "matin.dzhumanov123"
    
    # Create a password that you can remember
    password = "AdminPass123!"  # You can change this to any password you want
    
    # Check if user already exists
    existing_user = user_collection.find_one({"email": email})
    if existing_user:
        print(f"User with email {email} already exists.")
        return None
    
    # Create user
    user_id = generate_uuid()
    created_date = datetime.now()
    
    user = {
        "id": user_id,
        "username": username,
        "email": email,
        "hashed_password": hash_password(password),
        "active": True,
        "verified": True,  # User is verified
        "created": created_date,
        "updated": None,
        "role": "admin"  # Admin privileges
    }
    
    user_collection.insert_one(user)
    print(f"Created admin user: {email}")
    
    # Create user profile
    profile = {
        "id": generate_uuid(),
        "user_id": user_id,
        "first_name": first_name,
        "last_name": last_name,
        "display_name": f"{first_name} {last_name}",
        "avatar": None,
        "phone_number": None,  # You can add a phone number if needed
        "timezone": "UTC",  # Default timezone
        "temperature_unit": "C",  # Default temperature unit
        "dark_mode": True,  # Default theme preference
        "favorite_devices": [],
        "created": created_date,
        "updated": None
    }
    
    profile_collection.insert_one(profile)
    print(f"Created profile for {first_name} {last_name}")
    
    return {
        "user": user,
        "profile": profile,
        "password": password  # Return plain text password for login
    }

# Main function
def seed_single_admin():
    print("Creating admin user...")
    
    user_data = create_admin_user()
    
    if user_data:
        print("\nAdmin user created successfully!")
        print(f"""
        User Details:
        - Email: {user_data['user']['email']}
        - Username: {user_data['user']['username']}
        - Password: {user_data['password']}
        - Role: {user_data['user']['role']}
        - Verified: {user_data['user']['verified']}
        - Name: {user_data['profile']['first_name']} {user_data['profile']['last_name']}
        """)
    else:
        print("Failed to create admin user.")

if __name__ == "__main__":
    seed_single_admin()
