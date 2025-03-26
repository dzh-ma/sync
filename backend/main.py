from fastapi import FastAPI, HTTPException, Body, Depends, BackgroundTasks, Request, Response
from fastapi.responses import FileResponse
from motor.motor_asyncio import AsyncIOMotorClient
from passlib.context import CryptContext
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import random
import datetime as dt
from datetime import datetime, timedelta, time, date
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from bson import ObjectId
import asyncio
import threading
import time as time_module
from typing import List, Optional, Dict, Any, Union
import os
import json
import uuid
from enum import Enum
from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
from reportlab.lib import colors
from enhanced_report_generator import generate_energy_report

# Initialize FastAPI
app = FastAPI()

# Database connection
client = AsyncIOMotorClient("mongodb://localhost:27017")
db = client.project_testmain
devices_collection = db['devices']
user_devices_collection = db['user_devices']  # New collection to link users and devices
permissions_collection = db['permissions']  # New collection for permissions
admin_users_collection = db['admin_users']
household_members_collection = db['household_members']
statistics_collection = db['statistics']  # New collection for energy statistics
reports_collection = db['reports']

async def set_default_permissions(household_id, email):
    default_permissions = {
        "household_id": household_id,
        "admin_email": email,
        "permissions": {
            "notifications": True,
            "energyAlerts": True,
            "addAutomation": True,
            "statisticalData": True,
            "deviceControl": True,
            "roomControl": True
        }
    }
    await permissions_collection.insert_one(default_permissions)


# Password hashing
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# CORS setup
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Utility functions for password handling
def verify_password(plain_password, hashed_password):
    return pwd_context.verify(plain_password, hashed_password)

def get_password_hash(password):
    return pwd_context.hash(password)

# Generate a 6-digit OTP
def generate_otp():
    return str(random.randint(10000, 99999))

# Send email function
def send_email(to_email, otp):
    from_email = "test@peakstudios.ae"
    password = "synchome123!"  # Replace with your actual email password

    # HTML email body
    html = f"""
    <html>
        <body style="font-family: Arial, sans-serif; background-color: #f4f4f9; padding: 20px;">
            <div style="max-width: 600px; margin: auto; background-color: white; border-radius: 10px; padding: 30px; box-shadow: 0 4px 10px rgba(0, 0, 0, 0.1);">
                <div style="text-align: center;">
                    <!-- App Logo (replace with actual logo path or URL) -->
                    <!--img src="https://tinypic.host/image/Sync-Logo.33m7pu" alt="SYNC Logo" style="width: 120px; margin-bottom: 20px;"-->
                </div>
                <h2 style="color: #1e40af; text-align: center;">SYNC</h2>
                <h3 style="color: #ff8c00; text-align: center;">Your OTP Code</h3>
                <p style="color: #555; font-size: 16px; line-height: 1.5;">
                    Hello,<br><br>
                    Your OTP code is <strong style="font-size: 20px; color: #1e40af;">{otp}</strong>.<br>
                    It is valid for the next 5 minutes.<br><br>
                    Please do not share this code with anyone.<br><br>
                    Thank you for using <strong style="color: #ff8c00;">SYNC</strong>!
                </p>
                <footer style="text-align: center; color: #aaa; font-size: 12px; margin-top: 30px;">
                    <p>SYNC - Smart Home App</p>
                </footer>
            </div>
        </body>
    </html>
    """

    # Create a multipart message
    msg = MIMEMultipart()
    msg['From'] = from_email
    msg['To'] = to_email
    msg['Subject'] = 'Your OTP Code'

    # Attach HTML content to the email
    msg.attach(MIMEText(html, 'html'))

    try:
        with smtplib.SMTP('smtp.titan.email', 587) as server:
            server.starttls()
            server.login(from_email, password)
            server.sendmail(from_email, to_email, msg.as_string())
        print(f"OTP email sent successfully to {to_email}!")
    except Exception as e:
        print(f"Failed to send OTP email: {e}")
        raise HTTPException(status_code=500, detail="Failed to send email")

# Send forgot password email function
def send_forgot_password_email(to_email, otp):
    from_email = "test@peakstudios.ae"
    password = "synchome123!"  # Replace with your actual email password

    # HTML email body for forgot password
    html = f"""
    <html>
        <body style="font-family: Arial, sans-serif; background-color: #f4f4f9; padding: 20px;">
            <div style="max-width: 600px; margin: auto; background-color: white; border-radius: 10px; padding: 30px; box-shadow: 0 4px 10px rgba(0, 0, 0, 0.1);">
                <div style="text-align: center;">
                    <!-- App Logo (replace with actual logo path or URL) -->
                    <img src="https://tinypic.host/image/Sync-Logo.33m7pu" alt="SYNC Logo" style="width: 120px; margin-bottom: 20px;">
                </div>
                <h2 style="color: #1e40af; text-align: center;">SYNC</h2>
                <h3 style="color: #ff8c00; text-align: center;">Password Reset Request</h3>
                <p style="color: #555; font-size: 16px; line-height: 1.5;">
                    Hello,<br><br>
                    We received a request to reset your password. Your OTP code is <strong style="font-size: 20px; color: #1e40af;">{otp}</strong>.<br>
                    It is valid for the next 5 minutes.<br><br>
                    If you did not request a password reset, please ignore this email.<br><br>
                    Thank you for using <strong style="color: #ff8c00;">SYNC</strong>!
                </p>
                <footer style="text-align: center; color: #aaa; font-size: 12px; margin-top: 30px;">
                    <p>SYNC - Smart Home App</p>
                </footer>
            </div>
        </body>
    </html>
    """

    # Create a multipart message
    msg = MIMEMultipart()
    msg['From'] = from_email
    msg['To'] = to_email
    msg['Subject'] = 'Password Reset OTP'

    # Attach HTML content to the email
    msg.attach(MIMEText(html, 'html'))

    try:
        with smtplib.SMTP('smtp.titan.email', 587) as server:
            server.starttls()
            server.login(from_email, password)
            server.sendmail(from_email, to_email, msg.as_string())
        print(f"Password reset email sent successfully to {to_email}!")
    except Exception as e:
        print(f"Failed to send password reset email: {e}")
        raise HTTPException(status_code=500, detail="Failed to send email")

# Registration endpoint
@app.post("/register")
async def register_user(data: dict = Body(...)):
    admin_email = data.get("email")
    password = data.get("password")

    # Check if the admin_email is already registered
    user = await db.admin_users.find_one({"admin_email": admin_email})
    if user:
        raise HTTPException(status_code=400, detail="Email already registered")

    # Generate a unique household ID
    household_id = str(ObjectId())

    # Hash the password and store the user in the database
    hashed_password = get_password_hash(password)
    await db.admin_users.insert_one({
        "admin_email": admin_email,
        "password": hashed_password,
        "household_id": household_id
    })

    return {"msg": "User registered successfully", "household_id": household_id}

# OTP request and verification schemas
class OTPRequest(BaseModel):
    email: str

class OTPVerify(BaseModel):
    email: str
    otp: str

# Request OTP API
@app.post("/request-otp")
async def request_otp(data: OTPRequest):
    admin_email = data.email
    otp = generate_otp()
    expires_at = datetime.utcnow() + timedelta(minutes=5)

    # Update the user's document with the OTP and expiration
    result = await db.admin_users.update_one(
        {"admin_email": admin_email},
        {"$set": {"otp": otp, "otp_expires_at": expires_at}}
    )

    if result.matched_count == 0:
        raise HTTPException(status_code=404, detail="User not found")

    # Send the OTP email
    send_email(admin_email, otp)
    return {"msg": "OTP sent to your email"}

# Verify OTP API
@app.post("/verify-otp")
async def verify_otp(data: OTPVerify):
    admin_email = data.email
    otp = data.otp

    # Retrieve the user's data
    user = await db.admin_users.find_one({"admin_email": admin_email})

    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    # Check if the OTP matches and is not expired
    if user.get("otp") != otp:
        raise HTTPException(status_code=400, detail="Invalid OTP")
    if datetime.utcnow() > user.get("otp_expires_at"):
        raise HTTPException(status_code=400, detail="OTP has expired")

    # Clear the OTP after successful verification
    await db.admin_users.update_one(
        {"admin_email": admin_email},
        {"$unset": {"otp": "", "otp_expires_at": ""}}
    )

    return {"msg": "OTP verified successfully", "success": True}

# Login Schema
class LoginRequest(BaseModel):
    email: str
    password: str

# Login endpoint
@app.post("/login")
async def login_user(data: LoginRequest):
    admin_email = data.email
    password = data.password

    user = await db.admin_users.find_one({"admin_email": admin_email})
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    if not verify_password(password, user["password"]):
        raise HTTPException(status_code=401, detail="Invalid password")

    #Add first name and last name to response
    return {
        "msg": "Login successful",
        "user_id": str(user["_id"]),  # Convert ObjectId to string
        "admin_email": user["admin_email"],
        "household_id": user["household_id"],
        "firstName": user.get("firstName"),
        "lastName": user.get("lastName")
    }

# Forgot Password - Request OTP
@app.post("/request-forgot-password-otp")
async def request_forgot_password_otp(data: OTPRequest):
    admin_email = data.email
    user = await db.admin_users.find_one({"admin_email": admin_email})
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    otp = generate_otp()
    expires_at = datetime.utcnow() + timedelta(minutes=5)
    await db.admin_users.update_one({"admin_email": admin_email}, {"$set": {"otp": otp, "otp_expires_at": expires_at}})
    send_forgot_password_email(admin_email, otp)

    return {"msg": "OTP sent to your email"}

# Forgot Password - Verify OTP
@app.post("/verify-forgot-password-otp")
async def verify_forgot_password_otp(data: OTPVerify):
    admin_email, otp = data.email, data.otp
    user = await db.admin_users.find_one({"admin_email": admin_email})
    if not user or user.get("otp") != otp or user.get("otp_expires_at") < datetime.utcnow():
        raise HTTPException(status_code=400, detail="Invalid or expired OTP")
    return {"msg": "OTP verified successfully"}

# Forgot Password - Reset Password
@app.post("/reset-password")
async def reset_password(data: dict = Body(...)):
    admin_email, new_password = data.get("email"), data.get("password")
    hashed_password = get_password_hash(new_password)
    await db.admin_users.update_one({"admin_email": admin_email}, {"$set": {"password": hashed_password}})
    return {"msg": "Password reset successfully"}

# Add to your existing schemas
class PersonalDetailsRequest(BaseModel):
    email: str
    firstName: str
    lastName: str
    phoneNumber: str
    gender: str
    birthdate: dict  # {day: int, month: int, year: int}
    country: str
    city: str
    address: str
    avatar: Optional[str] = None

# Add this endpoint with your existing routes
@app.post("/register_personal")
async def register_personal(data: PersonalDetailsRequest):
    try:
        # Convert birthdate components to date object
        birthdate = datetime(
            year=data.birthdate["year"],
            month=data.birthdate["month"],
            day=data.birthdate["day"]
        )

        # Update user with personal details
        result = await db.admin_users.find_one_and_update(
            {"admin_email": data.email},
            {"$set": {
                "firstName": data.firstName,
                "lastName": data.lastName,
                "phoneNumber": data.phoneNumber,
                "gender": data.gender,
                "birthdate": birthdate,
                "country": data.country,
                "city": data.city,
                "address": data.address,
                "avatar": data.avatar
            }},
            return_document=True
        )

        if not result:
            raise HTTPException(status_code=404, detail="User not found")

        await set_default_permissions(result["household_id"], data.email)

        # Convert ObjectId to string
        result["_id"] = str(result["_id"])

        return {"msg": "Personal details saved successfully", "user": result}

    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

# Define request body models
class AddDeviceRequest(BaseModel):
    user_id: str
    device_name: str
    deviceType: str
    room: str
    household_id: str
    base_power_consumption: Optional[float] = None
    settings: Optional[dict] = None

class TrackEnergyRequest(BaseModel):
    user_id: str
    device_name: str
    hours: int

# Update endpoints to use request body models
@app.get("/api/user/devices")
async def get_user_devices(user_id: str, household_id: str = None):
    query = {'user_id': user_id}
    if household_id:
        query['household_id'] = household_id
    
    user_devices = await user_devices_collection.find(
        query,
        {'_id': 0}
    ).to_list(length=100)

    transformed_devices = [
        {
            "name": device["device_name"], 
            "base_power_consumption": device["energy_usage_per_hour"],  # Rename for clarity
            "type": device.get("deviceType", "unknown"),
            "room": device.get("room", "unknown"),
            "status": device.get("status", "off"),
            "total_energy_consumed": device.get("total_energy_consumed", 0.0),
            "settings": device.get("settings", {}),  # Include settings for brightness, temperature, speed
            "last_status_change": device.get("last_status_change", datetime.now())
        }
        for device in user_devices
    ]
    return transformed_devices

@app.post("/api/user/track")
async def track_user_energy(data: TrackEnergyRequest):
    device = await devices_collection.find_one({'name': data.device_name})
    if device:
        energy_used = device['energy_usage_per_hour'] * data.hours
        return {"energy_used": energy_used}
    raise HTTPException(status_code=404, detail="Device not found")

# Dictionary mapping device types to realistic power consumption (W)
device_energy_usage = {
    "LED Light Bulb": (5, 15),
    "Incandescent Bulb": (40, 100),
    "Smart Plug": (1, 3),
    "Smart Lock": (0.1, 2),
    "TV": (40, 250),
    "Gaming Console": (50, 300),
    "Laptop Charger": (30, 100),
    "Desktop PC": (150, 800),
    "WiFi Router": (5, 20),
    "Smart Speaker": (3, 15),
    "Coffee Maker": (600, 1200),
    "Microwave": (600, 1500),
    "Refrigerator": (100, 800),
    "Blender": (300, 1500),
    "Dishwasher": (1200, 2400),
    "Air Conditioner": (500, 3500),
    "Ceiling Fan": (10, 75),
    "Smart Thermostat": (1, 5),
    "Washing Machine": (500, 2000),
    "Dryer": (1500, 5000),
    "Electric Heater": (500, 2500),
    "Dehumidifier": (200, 800),
    "Water Heater": (1000, 5000),
    "Smart Camera": (2, 10),
    "Video Doorbell": (2, 10),
    "Motion Sensor": (0.5, 3),
    "Smart Alarm System": (3, 15),
}

@app.post("/api/user/add-device")
async def add_device_to_user(data: AddDeviceRequest):
    try:
        # Validate that the device name, type, and room are provided
        if not data.device_name:
            raise HTTPException(status_code=400, detail={"message": "Device name is required"})
        if not data.deviceType:
            raise HTTPException(status_code=400, detail={"message": "Device type is required"})
        if not data.room:
            raise HTTPException(status_code=400, detail={"message": "Room is required"})

        # Validate user existence
        admin_user = None
        household_member = None
        
        try:
            if ObjectId.is_valid(data.user_id):
                admin_user = await admin_users_collection.find_one({"_id": ObjectId(data.user_id)})
        except:
            pass
            
        if not admin_user:
            household_member = await household_members_collection.find_one({"email": data.user_id})
        
        if not admin_user and not household_member:
            raise HTTPException(
                status_code=404,
                detail={"message": "User not found", "device": data.device_name}
            )
            
        # Check permissions
        has_permission = False
        
        if admin_user:
            admin_permissions = await permissions_collection.find_one({"admin_email": admin_user.get("admin_email")})
            if admin_permissions and admin_permissions.get("permissions", {}).get("deviceControl"):
                has_permission = True
        elif household_member:
            member_permissions = household_member.get("permissions", {})
            if member_permissions.get("deviceControl"):
                has_permission = True
                
        if not has_permission:
            raise HTTPException(
                status_code=403,
                detail={"message": "You don't have permission to add devices"}
            )

        # Use provided base_power_consumption if available
        energy_usage_per_hour = data.base_power_consumption
        
        if energy_usage_per_hour is None:
            # Map frontend device types to the realistic dataset
            device_type_map = {
                "light": "LED Light Bulb",
                "thermostat": "Smart Thermostat",
                "fan": "Ceiling Fan",
                "tv": "TV",
                "lock": "Smart Lock",
                "plug": "Smart Plug",
                "coffee_maker": "Coffee Maker",
                "microwave": "Microwave",
                "refrigerator": "Refrigerator",
                "washing_machine": "Washing Machine"
            }

            # Get the mapped device type or use the provided type directly
            mapped_device_type = device_type_map.get(data.deviceType, data.deviceType)
            
            # Assign energy consumption based on the device type from device_energy_usage
            if mapped_device_type in device_energy_usage:
                min_usage, max_usage = device_energy_usage[mapped_device_type]
                # Use random value within the range instead of the average
                energy_usage_per_hour = random.uniform(min_usage, max_usage)
            else:
                energy_usage_per_hour = 10  # Fallback default if type not found

        # Extract settings from the request or use defaults
        settings = data.settings or {}
        if not settings.get("brightness") and data.deviceType == "light":
            settings["brightness"] = 80
        if not settings.get("temperature") and data.deviceType == "thermostat":
            settings["temperature"] = 22
        if not settings.get("speed") and data.deviceType == "fan":
            settings["speed"] = 2

        # Insert the device with calculated energy usage into user_devices_collection
        device_doc = {
            "user_id": data.user_id,
            "device_name": data.device_name,
            "energy_usage_per_hour": round(float(energy_usage_per_hour), 1),  # Round to 1 decimal place
            "household_id": data.household_id,
            "deviceType": data.deviceType,
            "room": data.room,
            "status": "off",  # Default status
            "total_energy_consumed": 0.0,
            "settings": settings,
            "last_status_change": str(datetime.now())  # Convert to string to avoid serialization issues
        }
        
        result = await user_devices_collection.insert_one(device_doc)

        return {
            "message": "Device added successfully", 
            "energy_usage_per_hour": energy_usage_per_hour,
            "id": str(result.inserted_id)
        }

    except HTTPException as he:
        raise he
    except Exception as e:
        print(f"Error adding device: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail={"message": "Internal server error", "error": str(e)}
        )

@app.post("/add-household-member")
async def add_household_member(data: dict = Body(...)):
    household_id = data.get("household_id")
    admin_user = data.get("admin_user")
    member_email = data.get("member_email")

    # Check if the household ID exists
    household = await db.admin_users.find_one({"household_id": household_id})
    if not household:
        raise HTTPException(status_code=404, detail="Household not found")

    # Add the household member
    await db.household_members.insert_one({
        "household_id": household_id,
        "admin_user": admin_user,
        "email": member_email
    })

    return {"msg": "Household member added successfully"}


class CreateProfileRequest(BaseModel):
    name: str
    email: str
    account_type: str
    pin_option: str
    household_id: str
    admin_user: str
    pin: str  # Add pin to the request model
    permissions: dict

@app.post("/api/create-profile")
async def create_profile(data: dict):
    try:
        # Validate required fields
        required_fields = ["name", "email", "account_type", "household_id", "admin_user", "pin", "permissions"]
        for field in required_fields:
            if field not in data:
                raise HTTPException(
                    status_code=400,
                    detail={"message": f"Missing required field: {field}"}
                )
        
        # Check if email already exists
        existing_member = await db.household_members.find_one({"email": data["email"]})
        if existing_member:
            raise HTTPException(
                status_code=400,
                detail={"message": "A member with this email already exists"}
            )
        
        # Insert the new member with permissions directly included
        member_data = {
            "name": data["name"],
            "email": data["email"],
            "account_type": data["account_type"],
            "household_id": data["household_id"],
            "admin_user": data["admin_user"],
            "pin": data["pin"],
            "created_at": datetime.now(),
            # Include permissions directly in the member document
            "permissions": data["permissions"]
        }
        
        result = await db.household_members.insert_one(member_data)
        member_id = str(result.inserted_id)
        
        return {
            "message": "Profile created successfully",
            "member_id": member_id
        }
    
    except HTTPException as he:
        raise he
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail={"message": "Internal server error", "error": str(e)}
        )

@app.post("/api/set-pin")
async def set_pin(data: dict = Body(...)):
    email = data.get("email")
    pin = data.get("pin")

    # Update the member's document with the pin
    await db.household_members.update_one(
        {"email": email},
        {"$set": {"pin": pin}}
    )

    return {"msg": "Pin set successfully"}

# Helper function to get user permissions
async def get_user_permissions(email: str):
    permissions_doc = await permissions_collection.find_one({"admin_email": email})
    if permissions_doc:
        return permissions_doc["permissions"]
    return None # Or return default permissions


# Fetch user details - for use on Dashboard page
@app.get("/api/user/{user_id}")
async def get_user(user_id: str):
    user = await admin_users_collection.find_one({"_id": ObjectId(user_id)})
    if user:
      user["_id"] = str(user["_id"])
      return {
          "_id": user["_id"],
            "admin_email": user["admin_email"],
            "household_id": user["household_id"],
            "firstName": user.get("firstName"),
            "lastName": user.get("lastName"),
            "phoneNumber": user.get("phoneNumber"),
            "gender": user.get("gender"),
            "birthdate": user.get("birthdate"),
            "country": user.get("country"),
            "city": user.get("city"),
            "address": user.get("address"),
            "avatar": user.get("avatar")  # Include avatar in response
      }
    else:
      raise HTTPException(status_code=404, detail="User not found")

@app.get("/api/permissions/{email}")
async def get_permissions(email: str):

    permissions = await get_user_permissions(email)
    if permissions:
        return permissions
    else:
        raise HTTPException(status_code=404, detail="Permissions not found")

@app.get("/api/household-members")
async def get_household_members(household_id: str):
    try:
        # Fetch all members for this household
        members = await db.household_members.find({"household_id": household_id}).to_list(length=100)
        
        # Transform the members to include string IDs
        transformed_members = []
        for member in members:
            member["id"] = str(member["_id"])
            del member["_id"]
            transformed_members.append(member)
            
        return transformed_members
    
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail={"message": "Internal server error", "error": str(e)}
        )

@app.delete("/api/household-members/delete")
async def delete_household_member(member_id: str, household_id: str):
    try:
        # Check if the member exists
        member = await db.household_members.find_one({"_id": ObjectId(member_id), "household_id": household_id})
        
        if not member:
            raise HTTPException(
                status_code=404,
                detail={"message": "Member not found"}
            )
        
        # Delete the member
        result = await db.household_members.delete_one({"_id": ObjectId(member_id)})
        
        if result.deleted_count == 0:
            raise HTTPException(
                status_code=500,
                detail={"message": "Failed to delete member"}
            )
        
        return {"message": "Member deleted successfully"}
    
    except HTTPException as he:
        raise he
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail={"message": "Internal server error", "error": str(e)}
        )

class UpdateProfileRequest(BaseModel):
  name: str
  email: str
  role: str

@app.get("/api/household-member/{email}")
async def get_household_member(email: str):
  member = await household_members_collection.find_one({"email":email})
  if member:
    member["_id"] = str(member["_id"])
    return member
  else:
    raise HTTPException(status_code=404, detail="Household member not found")

@app.put("/api/update-household-member/{email}")
async def update_household_member(email:str, member: UpdateProfileRequest):
    updated_member = await household_members_collection.find_one_and_update({"email": email},
                                                                              {"$set": member.dict()},
                                                                              return_document=True)
    if updated_member:
      updated_member["_id"] = str(updated_member["_id"])
      return updated_member
    else:
        raise HTTPException(status_code=404, detail="Household member not found")

class UpdatePermissionRequest(BaseModel):
  permissions: dict

@app.get("/api/permissions-member/{email}")
async def get_member_permissions(email: str):
  permission = await permissions_collection.find_one({"admin_email":email})
  if permission:
    permission["_id"] = str(permission["_id"])
    return permission
  else:
    raise HTTPException(status_code=404, detail="Household member not found")

@app.put("/api/update-permissions-member/{email}")
async def update_member_permissions(email:str, permission: UpdatePermissionRequest):
  update_permission = await permissions_collection.find_one_and_update({"admin_email": email},
                                                                            {"$set": permission.dict()},
                                                                            return_document=True)
  if update_permission:
    update_permission["_id"] = str(update_permission["_id"])
    return update_permission
  else:
    raise HTTPException(status_code=404, detail="Household member not found")

@app.post("/api/user/update-device-settings")
async def update_device_settings(data: dict = Body(...)):
    try:
        user_id = data.get("user_id")
        household_id = data.get("household_id")
        device_name = data.get("device_name")
        settings = data.get("settings", {})
        calculated_power = data.get("calculated_power")  # Get the calculated power from frontend
        
        if not user_id or not device_name:
            raise HTTPException(
                status_code=400,
                detail={"message": "Missing required fields"}
            )
        
        # Find the device
        device = await user_devices_collection.find_one({
            "user_id": user_id,
            "device_name": device_name,
            "household_id": household_id
        })
        
        if not device:
            raise HTTPException(
                status_code=404,
                detail={"message": "Device not found"}
            )
        
        # Update the device settings
        update_data = {}
        for key, value in settings.items():
            update_data[f"settings.{key}"] = value
        
        # Add last_updated timestamp
        update_data["last_updated"] = datetime.now()
        
        # Update power consumption if provided and device is on
        if calculated_power is not None and device.get("status") == "on":
            update_data["energy_usage_per_hour"] = calculated_power
        
        result = await user_devices_collection.update_one(
            {"_id": device["_id"]},
            {"$set": update_data}
        )
        
        if result.modified_count == 0:
            raise HTTPException(
                status_code=500,
                detail={"message": "Failed to update device settings"}
            )
        
        return {"message": "Device settings updated successfully"}
    
    except HTTPException as he:
        raise he
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail={"message": "Internal server error", "error": str(e)}
        )

@app.delete("/api/user/delete-device")
async def delete_device(user_id: str, device_name: str, household_id: str = None):
    try:
        # Find the device
        device = await user_devices_collection.find_one({
            "user_id": user_id,
            "device_name": device_name,
            "household_id": household_id
        })
        
        if not device:
            raise HTTPException(
                status_code=404,
                detail={"message": "Device not found"}
            )
        
        # Delete the device
        result = await user_devices_collection.delete_one({"_id": device["_id"]})
        
        if result.deleted_count == 0:
            raise HTTPException(
                status_code=500,
                detail={"message": "Failed to delete device"}
            )
        
        # Also remove from local_devices if present
        local_devices = await db.local_devices.find_one({"user_id": user_id})
        if local_devices and "devices" in local_devices:
            updated_devices = [d for d in local_devices["devices"] if d["name"] != device_name and d["id"] != device_name]
            await db.local_devices.update_one(
                {"user_id": user_id},
                {"$set": {"devices": updated_devices}}
            )
        
        return {"message": "Device deleted successfully"}
    
    except HTTPException as he:
        raise he
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail={"message": "Internal server error", "error": str(e)}
        )

class UpdateDeviceRequest(BaseModel):
    user_id: str
    old_device_name: str
    new_device_name: str
    room: str
    household_id: str

@app.put("/api/user/update-device")
async def update_user_device(data: UpdateDeviceRequest):
    try:
        # Check if the device exists for this user
        device = await user_devices_collection.find_one({
            "user_id": data.user_id,
            "device_name": data.old_device_name,
            "household_id": data.household_id
        })
        
        if not device:
            raise HTTPException(
                status_code=404,
                detail={"message": "Device not found"}
            )
        
        # Update the device
        result = await user_devices_collection.update_one(
            {
                "user_id": data.user_id,
                "device_name": data.old_device_name,
                "household_id": data.household_id
            },
            {
                "$set": {
                    "device_name": data.new_device_name,
                    "room": data.room
                }
            }
        )
        
        if result.modified_count == 0:
            raise HTTPException(
                status_code=500,
                detail={"message": "Failed to update device"}
            )
        
        return {"message": "Device updated successfully"}
    
    except HTTPException as he:
        raise he
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail={"message": "Internal server error", "error": str(e)}
        )

@app.put("/api/user/toggle-device")
async def toggle_device_endpoint(
    user_id: str, 
    device_name: str, 
    household_id: str = None, 
    status: str = None
):
    try:
        print(f"Toggling device {device_name} to {status} for user {user_id}")
        
        # Find the device
        device = await user_devices_collection.find_one({
            "user_id": user_id,
            "device_name": device_name,
            "household_id": household_id
        })
        
        if not device:
            print(f"Device not found: {device_name}")
            raise HTTPException(
                status_code=404,
                detail={"message": "Device not found"}
            )
        
        # Calculate energy consumption if turning off
        total_energy_consumed = device.get("total_energy_consumed", 0.0)
        last_status_change = device.get("last_status_change", datetime.now())
        
        if device["status"] == "on" and status == "off":
            time_on_hours = (datetime.now() - last_status_change).total_seconds() / 3600  # Convert to hours
            energy_used = device["energy_usage_per_hour"] * time_on_hours / 1000  # Convert W to kWh
            total_energy_consumed += energy_used
        
        # Update the device status and energy data
        await user_devices_collection.update_one(
            {
                "user_id": user_id,
                "device_name": device_name,
                "household_id": household_id
            },
            {
                "$set": {
                    "status": status,
                    "total_energy_consumed": total_energy_consumed,
                    "last_status_change": datetime.now()  # Update timestamp
                }
            }
        )
        
        print(f"Device {device_name} toggled to {status}")
    
    except HTTPException as he:
        raise he
    except Exception as e:
        print(f"Error toggling device: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail={"message": "Internal server error", "error": str(e)}
        )

# Add Room model
class RoomRequest(BaseModel):
    name: str
    type: str
    household_id: str
    image: str = "/minimal2.png"

# Add room endpoints
@app.post("/api/rooms/add")
async def add_room(data: RoomRequest):
    try:
        # Validate that the room name is provided
        if not data.name:
            raise HTTPException(status_code=400, detail={"message": "Room name is required"})
        if not data.type:
            raise HTTPException(status_code=400, detail={"message": "Room type is required"})
        if not data.household_id:
            raise HTTPException(status_code=400, detail={"message": "Household ID is required"})
        
        # Check if room already exists in this household
        existing_room = await db.rooms.find_one({
            "name": data.name,
            "household_id": data.household_id
        })
        
        if existing_room:
            raise HTTPException(
                status_code=400,
                detail={"message": "A room with this name already exists in your household"}
            )
        
        # Insert the room
        room_data = {
            "name": data.name,
            "type": data.type,
            "household_id": data.household_id,
            "image": data.image
        }
        
        result = await db.rooms.insert_one(room_data)
        
        # Return the created room with its ID
        return {
            "message": "Room added successfully",
            "room": {
                "id": str(result.inserted_id),
                "name": data.name,
                "type": data.type,
                "image": data.image
            }
        }
    
    except HTTPException as he:
        raise he
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail={"message": "Internal server error", "error": str(e)}
        )

@app.get("/api/rooms")
async def get_rooms(household_id: str):
    try:
        rooms = await db.rooms.find({"household_id": household_id}).to_list(length=100)
        
        # Transform the rooms to include string IDs
        transformed_rooms = []
        for room in rooms:
            room["id"] = str(room["_id"])
            del room["_id"]
            transformed_rooms.append(room)
            
        return transformed_rooms
    
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail={"message": "Internal server error", "error": str(e)}
        )

@app.delete("/api/rooms/delete")
async def delete_room(room_id: str, household_id: str):
    try:
        # Check if the room exists
        room = await db.rooms.find_one({"_id": ObjectId(room_id), "household_id": household_id})
        
        if not room:
            raise HTTPException(
                status_code=404,
                detail={"message": "Room not found"}
            )
        
        # Delete the room
        result = await db.rooms.delete_one({"_id": ObjectId(room_id)})
        
        if result.deleted_count == 0:
            raise HTTPException(
                status_code=500,
                detail={"message": "Failed to delete room"}
            )
        
        return {"message": "Room deleted successfully"}
    
    except HTTPException as he:
        raise he
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail={"message": "Internal server error", "error": str(e)}
        )

@app.get("/api/permissions/{member_id}")
async def get_permissions(member_id: str):
    try:
        # Find the member
        member = await db.household_members.find_one({"_id": ObjectId(member_id)})
        
        if not member or "permissions" not in member:
            # Return default permissions if none found
            return {
                "notifications": True,
                "energyAlerts": True,
                "addAutomation": False,
                "statisticalData": False,
                "deviceControl": True,
                "roomControl": False
            }
        
        # Return the permissions from the member document
        return member["permissions"]
    
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail={"message": "Internal server error", "error": str(e)}
        )

@app.post("/api/permissions/update")
async def update_permissions(data: dict):
    try:
        member_id = data.get("member_id")
        household_id = data.get("household_id")
        permissions = data.get("permissions")
        
        if not member_id or not household_id or not permissions:
            raise HTTPException(
                status_code=400,
                detail={"message": "Missing required fields"}
            )
        
        # Check if the member exists
        member = await db.household_members.find_one({"_id": ObjectId(member_id), "household_id": household_id})
        
        if not member:
            raise HTTPException(
                status_code=404,
                detail={"message": "Member not found"}
            )
        
        # Update permissions directly in the household_members collection
        result = await db.household_members.update_one(
            {"_id": ObjectId(member_id)},
            {"$set": {"permissions": permissions}}
        )
        
        if result.modified_count == 0:
            raise HTTPException(
                status_code=500,
                detail={"message": "Failed to update permissions"}
            )
        
        return {"message": "Permissions updated successfully"}
    
    except HTTPException as he:
        raise he
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail={"message": "Internal server error", "error": str(e)}
        )

@app.post("/api/household-members/update-pin")
async def update_member_pin(data: dict):
    try:
        member_id = data.get("member_id")
        household_id = data.get("household_id")
        pin = data.get("pin")
        
        if not member_id or not household_id or not pin:
            raise HTTPException(
                status_code=400,
                detail={"message": "Missing required fields"}
            )
        
        # Check if the member exists
        member = await db.household_members.find_one({"_id": ObjectId(member_id), "household_id": household_id})
        
        if not member:
            raise HTTPException(
                status_code=404,
                detail={"message": "Member not found"}
            )
        
        # Update the PIN
        result = await db.household_members.update_one(
            {"_id": ObjectId(member_id)},
            {"$set": {"pin": pin}}
        )
        
        if result.modified_count == 0:
            raise HTTPException(
                status_code=500,
                detail={"message": "Failed to update PIN"}
            )
        
        return {"message": "PIN updated successfully"}
    
    except HTTPException as he:
        raise he
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail={"message": "Internal server error", "error": str(e)}
        )

@app.post("/api/household-members/update")
async def update_household_member(data: dict):
    try:
        member_id = data.get("member_id")
        household_id = data.get("household_id")
        
        if not member_id or not household_id:
            raise HTTPException(
                status_code=400,
                detail={"message": "Missing required fields"}
            )
        
        # Check if the member exists
        member = await db.household_members.find_one({"_id": ObjectId(member_id), "household_id": household_id})
        
        if not member:
            raise HTTPException(
                status_code=404,
                detail={"message": "Member not found"}
            )
        
        # Remove these fields from the update
        if "member_id" in data:
            del data["member_id"]
        if "household_id" in data:
            del data["household_id"]
        
        # Update the member
        result = await db.household_members.update_one(
            {"_id": ObjectId(member_id)},
            {"$set": data}
        )
        
        if result.modified_count == 0:
            raise HTTPException(
                status_code=500,
                detail={"message": "Failed to update member"}
            )
        
        return {"message": "Member updated successfully"}
    
    except HTTPException as he:
        raise he
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail={"message": "Internal server error", "error": str(e)}
        )

@app.post("/api/household-login")
async def household_login(data: dict):
    try:
        email = data.get("email")
        pin = data.get("pin")
        
        if not email or not pin:
            raise HTTPException(
                status_code=400,
                detail={"message": "Email and PIN are required"}
            )
        
        # Find the household member
        member = await db.household_members.find_one({"email": email})
        
        if not member:
            raise HTTPException(
                status_code=401,
                detail={"message": "Invalid email or PIN"}
            )
        
        # Verify PIN
        stored_pin = str(member.get("pin", ""))  # Convert to string for comparison
        if stored_pin != str(pin):  # Convert input pin to string as well
            raise HTTPException(
                status_code=401,
                detail={"message": "Invalid email or PIN"}
            )
        
        # Make sure permissions are included in the response
        # If permissions are directly in the member document
        permissions = member.get("permissions", {
            "notifications": False,
            "energyAlerts": False,
            "addAutomation": False,
            "statisticalData": False,
            "deviceControl": False,
            "roomControl": False
        })
        
        # Print permissions for debugging
        print(f"Member permissions: {permissions}")
        
        # Return member data with permissions
        return {
            "member_id": str(member["_id"]),
            "name": member["name"],
            "email": member["email"],
            "account_type": member["account_type"],
            "household_id": member["household_id"],
            "permissions": permissions
        }
    
    except HTTPException as he:
        raise he
    except Exception as e:
        print(f"Login error: {str(e)}")  # Add logging for debugging
        raise HTTPException(
            status_code=500,
            detail={"message": "Internal server error", "error": str(e)}
        )

@app.get("/api/household-member/{member_id}")
async def get_household_member(member_id: str):
    try:
        # Find the member
        member = await db.household_members.find_one({"_id": ObjectId(member_id)})
        
        if not member:
            raise HTTPException(
                status_code=404,
                detail={"message": "Member not found"}
            )
        
        # Return member data with permissions
        return {
            "member_id": str(member["_id"]),
            "name": member["name"],
            "email": member["email"],
            "account_type": member["account_type"],
            "household_id": member["household_id"],
            "permissions": member.get("permissions", {
                "notifications": False,
                "energyAlerts": False,
                "addAutomation": False,
                "statisticalData": False,
                "deviceControl": False,
                "roomControl": False
            })
        }
    
    except HTTPException as he:
        raise he
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail={"message": "Internal server error", "error": str(e)}
        )

@app.get("/api/household-member/validate")
async def validate_household_member(member_id: str, required_permission: str):
    try:
        # Find the member
        member = await db.household_members.find_one({"_id": ObjectId(member_id)})
        
        if not member:
            return {"valid": False, "message": "Member not found"}
        
        # Get member permissions
        permissions = member.get("permissions", {})
        
        # Check if the member has the required permission
        has_permission = permissions.get(required_permission, False)
        
        return {
            "valid": has_permission,
            "message": "Access granted" if has_permission else "Access denied"
        }
    
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail={"message": "Internal server error", "error": str(e)}
        )

@app.get("/api/validate-permission")
async def validate_permission(user_id: str, permission: str):
    try:
        # Check if this is an admin user or household member
        admin_user = None
        household_member = None
        
        try:
            # Try to parse as ObjectId for admin users
            admin_user = await admin_users_collection.find_one({"_id": ObjectId(user_id)})
        except:
            # If not a valid ObjectId, check if it's an email for household members
            household_member = await household_members_collection.find_one({"email": user_id})
        
        if not admin_user and not household_member:
            return {"valid": False, "message": "User not found"}
        
        # Check permissions
        has_permission = False
        
        if admin_user:
            # Admin users might have permissions in a separate collection
            admin_permissions = await permissions_collection.find_one({"admin_email": admin_user["admin_email"]})
            if admin_permissions and admin_permissions.get("permissions", {}).get(permission):
                has_permission = True
        elif household_member:
            # Check if the household member has the required permission
            member_permissions = household_member.get("permissions", {})
            if member_permissions.get(permission):
                has_permission = True
                
        return {
            "valid": has_permission,
            "message": "Access granted" if has_permission else "Access denied"
        }
    
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail={"message": "Internal server error", "error": str(e)}
        )

# Add these models for automations
class AutomationSchedule(BaseModel):
    type: str  # "once", "daily", "weekly", "custom"
    startTime: str
    endTime: str
    daysOfWeek: Optional[List[int]] = None

class AutomationRequest(BaseModel):
    name: str
    description: str
    icon: str
    active: bool
    schedule: AutomationSchedule
    devices: List[str]
    user_id: str
    household_id: str

# Add these endpoints for automations
@app.post("/api/automations/create")
async def create_automation(data: AutomationRequest):
    try:
        # Create a unique ID for the automation
        automation_id = str(ObjectId())
        
        # Format the automation data
        automation = {
            "_id": ObjectId(automation_id),
            "name": data.name,
            "description": data.description,
            "icon": data.icon,
            "active": data.active,
            "schedule": {
                "type": data.schedule.type,
                "startTime": data.schedule.startTime,
                "endTime": data.schedule.endTime,
                "daysOfWeek": data.schedule.daysOfWeek
            },
            "devices": data.devices,
            "user_id": data.user_id,
            "household_id": data.household_id,
            "created_at": datetime.now()
        }
        
        # Insert the automation into the database
        await db.automations.insert_one(automation)
        
        # Return the created automation with string ID
        automation["_id"] = str(automation["_id"])
        
        # Schedule the automation if it's active
        if data.active:
            schedule_automation(automation)
        
        return {
            "message": "Automation created successfully",
            "automation": automation
        }
    
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail={"message": "Internal server error", "error": str(e)}
        )

@app.get("/api/automations")
async def get_automations(user_id: str, household_id: str = None):
    try:
        # Build query based on available parameters
        query = {'user_id': user_id}
        if household_id:
            query['household_id'] = household_id
        
        # Fetch automations from the database
        automations = await db.automations.find(query).to_list(length=100)
        
        # Convert ObjectId to string for each automation
        for automation in automations:
            automation["_id"] = str(automation["_id"])
        
        return automations
    
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail={"message": "Internal server error", "error": str(e)}
        )

class UpdateAdminProfileRequest(BaseModel):
    email: str
    firstName: Optional[str] = None
    lastName: Optional[str] = None
    phoneNumber: Optional[str] = None
    gender: Optional[str] = None
    birthdate: Optional[dict] = None  # {day: int, month: int, year: int}
    country: Optional[str] = None
    city: Optional[str] = None
    address: Optional[str] = None
    avatar: Optional[str] = None  # Allow updating avatar

@app.put("/api/update-admin-profile")
async def update_admin_profile(data: UpdateAdminProfileRequest):
    try:
        # Prepare update data, only including fields that are provided
        update_data = {}
        if data.firstName is not None:
            update_data["firstName"] = data.firstName
        if data.lastName is not None:
            update_data["lastName"] = data.lastName
        if data.phoneNumber is not None:
            update_data["phoneNumber"] = data.phoneNumber
        if data.gender is not None:
            update_data["gender"] = data.gender
        if data.birthdate is not None:
            birthdate = datetime(
                year=data.birthdate["year"],
                month=data.birthdate["month"],
                day=data.birthdate["day"]
            )
            update_data["birthdate"] = birthdate
        if data.country is not None:
            update_data["country"] = data.country
        if data.city is not None:
            update_data["city"] = data.city
        if data.address is not None:
            update_data["address"] = data.address
        if data.avatar is not None:
            update_data["avatar"] = data.avatar  # Update avatar if provided

        # Update the admin user's document
        result = await db.admin_users.find_one_and_update(
            {"admin_email": data.email},
            {"$set": update_data},
            return_document=True
        )

        if not result:
            raise HTTPException(status_code=404, detail="Admin user not found")

        # Convert ObjectId to string and return updated user
        result["_id"] = str(result["_id"])
        return {"message": "Admin profile updated successfully", "user": result}

    except HTTPException as he:
        raise he
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail={"message": "Internal server error", "error": str(e)}
        )
    
@app.put("/api/automations/update/{automation_id}")
async def update_automation(automation_id: str, data: AutomationRequest):
    try:
        # Check if the automation exists
        automation = await db.automations.find_one({"_id": ObjectId(automation_id)})
        
        if not automation:
            raise HTTPException(
                status_code=404,
                detail={"message": "Automation not found"}
            )
        
        # Update the automation
        updated_automation = {
            "name": data.name,
            "description": data.description,
            "icon": data.icon,
            "active": data.active,
            "schedule": {
                "type": data.schedule.type,
                "startTime": data.schedule.startTime,
                "endTime": data.schedule.endTime,
                "daysOfWeek": data.schedule.daysOfWeek
            },
            "devices": data.devices,
            "updated_at": datetime.now()
        }
        
        result = await db.automations.update_one(
            {"_id": ObjectId(automation_id)},
            {"$set": updated_automation}
        )
        
        if result.modified_count == 0:
            raise HTTPException(
                status_code=500,
                detail={"message": "Failed to update automation"}
            )
        
        # Get the updated automation
        updated = await db.automations.find_one({"_id": ObjectId(automation_id)})
        updated["_id"] = str(updated["_id"])
        
        # Re-schedule the automation if it's active
        if data.active:
            schedule_automation(updated)
        
        return {
            "message": "Automation updated successfully",
            "automation": updated
        }
    
    except HTTPException as he:
        raise he
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail={"message": "Internal server error", "error": str(e)}
        )

@app.delete("/api/automations/delete/{automation_id}")
async def delete_automation(automation_id: str):
    try:
        # Check if the automation exists
        automation = await db.automations.find_one({"_id": ObjectId(automation_id)})
        
        if not automation:
            raise HTTPException(
                status_code=404,
                detail={"message": "Automation not found"}
            )
        
        # Delete the automation
        result = await db.automations.delete_one({"_id": ObjectId(automation_id)})
        
        if result.deleted_count == 0:
            raise HTTPException(
                status_code=500,
                detail={"message": "Failed to delete automation"}
            )
        
        return {"message": "Automation deleted successfully"}
    
    except HTTPException as he:
        raise he
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail={"message": "Internal server error", "error": str(e)}
        )

@app.put("/api/automations/toggle/{automation_id}")
async def toggle_automation(automation_id: str, active: bool):
    try:
        # Check if the automation exists
        automation = await db.automations.find_one({"_id": ObjectId(automation_id)})
        
        if not automation:
            raise HTTPException(
                status_code=404,
                detail={"message": "Automation not found"}
            )
        
        # Update the automation's active status
        result = await db.automations.update_one(
            {"_id": ObjectId(automation_id)},
            {"$set": {"active": active}}
        )
        
        if result.modified_count == 0:
            raise HTTPException(
                status_code=500,
                detail={"message": "Failed to update automation status"}
            )
        
        # Get the updated automation
        updated = await db.automations.find_one({"_id": ObjectId(automation_id)})
        updated["_id"] = str(updated["_id"])
        
        # Re-schedule the automation if it's active
        if active:
            schedule_automation(updated)
        
        return {
            "message": "Automation status updated successfully",
            "automation": updated
        }
    
    except HTTPException as he:
        raise he
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail={"message": "Internal server error", "error": str(e)}
        )

# Global dictionary to store automation tasks
automation_tasks = {}

# Function to schedule an automation
def schedule_automation(automation):
    automation_id = str(automation["_id"])
    
    # Cancel any existing task for this automation
    if automation_id in automation_tasks:
        automation_tasks[automation_id].cancel()
        del automation_tasks[automation_id]
    
    # Only schedule if the automation is active
    if not automation["active"]:
        return
    
    # Create a task for this automation
    task = asyncio.create_task(run_automation(automation))
    automation_tasks[automation_id] = task

# Function to run an automation
async def run_automation(automation):
    try:
        automation_id = str(automation["_id"])
        schedule = automation["schedule"]
        devices = automation["devices"]
        user_id = automation["user_id"]
        household_id = automation["household_id"]
        
        while True:
            now = datetime.now()
            print(f"[{now}] Checking automation {automation_id}")
            
            start_time = parse_time(schedule["startTime"])
            end_time = parse_time(schedule["endTime"])
            
            should_run_today = True
            
            if schedule["type"] == "weekly" and schedule["daysOfWeek"]:
                today_weekday = now.weekday()
                should_run_today = today_weekday in schedule["daysOfWeek"]
                print(f"[{now}] Today is {today_weekday}, should run today: {should_run_today}")
            
            if should_run_today:
                start_datetime = datetime.combine(now.date(), start_time)
                end_datetime = datetime.combine(now.date(), end_time)
                
                if end_time < start_time:
                    end_datetime += timedelta(days=1)
                
                print(f"[{now}] Start time: {start_datetime}, End time: {end_datetime}")
                
                if now.time() < start_time:
                    seconds_until_start = (start_datetime - now).total_seconds()
                    print(f"[{now}] Waiting {seconds_until_start} seconds until start time")
                    await asyncio.sleep(seconds_until_start)
                    
                    for device_id in devices:
                        await toggle_device(user_id, device_id, household_id, "on")
                        print(f"[{now}] Device {device_id} turned on")
                    
                    seconds_until_end = (end_datetime - datetime.now()).total_seconds()
                    print(f"[{now}] Waiting {seconds_until_end} seconds until end time")
                    await asyncio.sleep(seconds_until_end)
                    
                    for device_id in devices:
                        await toggle_device(user_id, device_id, household_id, "off")
                        print(f"[{now}] Device {device_id} turned off")
                
                elif start_time <= now.time() < end_time:
                    for device_id in devices:
                        await toggle_device(user_id, device_id, household_id, "on")
                        print(f"[{now}] Device {device_id} turned on immediately")
                    
                    seconds_until_end = (end_datetime - now).total_seconds()
                    print(f"[{now}] Waiting {seconds_until_end} seconds until end time")
                    await asyncio.sleep(seconds_until_end)
                    
                    for device_id in devices:
                        await toggle_device(user_id, device_id, household_id, "off")
                        print(f"[{now}] Device {device_id} turned off")
            
            if schedule["type"] == "once":
                await db.automations.update_one(
                    {"_id": ObjectId(automation_id)},
                    {"$set": {"active": False}}
                )
                print(f"[{now}] Automation {automation_id} marked as inactive")
                break
            
            tomorrow = now.date() + timedelta(days=1)
            next_run = datetime.combine(tomorrow, start_time)
            seconds_until_next_run = (next_run - now).total_seconds()
            print(f"[{now}] Waiting {seconds_until_next_run} seconds until next run")
            await asyncio.sleep(seconds_until_next_run)
    
    except asyncio.CancelledError:
        print(f"[{now}] Automation {automation_id} task cancelled")
    except Exception as e:
        print(f"[{now}] Error in automation {automation_id}: {str(e)}")


# Helper function to parse time string
def parse_time(time_str):
    try:
        hours, minutes = map(int, time_str.split(':'))
        return time(hours, minutes)
    except (ValueError, TypeError, AttributeError):
        # Handle invalid time strings or None values
        print(f"Invalid time format: {time_str}")
        return time(0, 0)  # Default to midnight

# Helper function to toggle a device
async def toggle_device(user_id, device_id, household_id, status):
    try:
        device = await user_devices_collection.find_one({
            "user_id": user_id,
            "device_name": device_id,
            "household_id": household_id
        })
        
        if not device:
            print(f"Device not found: {device_id}")
            return
        
        last_status_change = device.get("last_status_change", datetime.now())
        energy_usage_per_hour = device.get("energy_usage_per_hour", 0)
        
        if device["status"] == "on" and status == "off":
            time_on_hours = (datetime.now() - last_status_change).total_seconds() / 3600
            energy_used = (energy_usage_per_hour * time_on_hours) / 1000
            total_energy_consumed = device.get("total_energy_consumed", 0) + energy_used
            print(f"Device {device_id} used {energy_used} kWh")
        else:
            total_energy_consumed = device.get("total_energy_consumed", 0)
        
        await user_devices_collection.update_one(
            {
                "user_id": user_id,
                "device_name": device_id,
                "household_id": household_id
            },
            {
                "$set": {
                    "status": status,
                    "total_energy_consumed": total_energy_consumed,
                    "last_status_change": datetime.now()
                }
            }
        )
        print(f"Device {device_id} toggled to {status}")
    except Exception as e:
        print(f"Error toggling device {device_id}: {str(e)}")

# Start a background task to load and schedule all active automations on startup
@app.on_event("startup")
async def startup_event():
    # Load all active automations
    automations = await db.automations.find({"active": True}).to_list(length=None)
    
    # Schedule each automation
    for automation in automations:
        schedule_automation(automation)
    
    # Start the statistics collection background task
    asyncio.create_task(collect_statistics_periodically())
    print("✅ Statistics collection background task started")

# Function to calculate and store energy statistics
async def collect_statistics():
    try:
        print("Collecting energy statistics...")
        
        # Get all user devices
        all_devices = await user_devices_collection.find({}).to_list(length=None)
        
        if not all_devices:
            print("No devices found for statistics collection")
            return
            
        # Group devices by household and user
        household_device_map = {}
        user_device_map = {}
        
        for device in all_devices:
            household_id = device.get('household_id')
            user_id = device.get('user_id')
            
            if household_id:
                if household_id not in household_device_map:
                    household_device_map[household_id] = []
                household_device_map[household_id].append(device)
            
            if user_id:
                if user_id not in user_device_map:
                    user_device_map[user_id] = []
                user_device_map[user_id].append(device)
        
        # Current timestamp
        current_time = datetime.now()
        current_date = current_time.date().isoformat()
        current_hour = current_time.hour
        
        # Process statistics for each household
        for household_id, devices in household_device_map.items():
            # Calculate energy metrics
            total_energy = 0
            device_type_energy = {}
            room_energy = {}
            
            for device in devices:
                device_name = device.get('device_name', device.get('name', 'Unknown Device'))
                device_type = device.get('deviceType', device.get('type', 'unknown'))
                device_room = device.get('room', 'unknown')
                device_status = device.get('status', 'off')
                energy_usage_per_hour = device.get('energy_usage_per_hour', device.get('base_power_consumption', 0))
                last_status_change = device.get('last_status_change')
                total_energy_consumed = device.get('total_energy_consumed', 0)
                
                # Calculate energy for this device
                device_energy = 0
                
                if device_status == 'on' and energy_usage_per_hour > 0:
                    # If device is on, calculate real-time energy consumption
                    if last_status_change:
                        last_change = datetime.fromisoformat(last_status_change.replace('Z', '+00:00')) if isinstance(last_status_change, str) else last_status_change
                        hours_since_on = (current_time - last_change).total_seconds() / 3600
                        device_energy = (energy_usage_per_hour * hours_since_on) / 1000  # Convert to kWh
                    else:
                        # Fallback: assume it's been on for the last hour
                        device_energy = energy_usage_per_hour / 1000
                else:
                    # If device is off, use stored total energy
                    device_energy = total_energy_consumed
                
                # Add to totals
                total_energy += device_energy
                
                # Add to device type map
                if device_type not in device_type_energy:
                    device_type_energy[device_type] = 0
                device_type_energy[device_type] += device_energy
                
                # Add to room map
                if device_room not in room_energy:
                    room_energy[device_room] = 0
                room_energy[device_room] += device_energy
            
            # Check if a daily record already exists for this household
            daily_record = await statistics_collection.find_one({
                'household_id': household_id,
                'date': current_date,
                'record_type': 'daily'
            })
            
            if daily_record:
                # Update existing daily record
                update_data = {
                    'last_updated': current_time,
                    'total_energy': total_energy,  # Replace with current total
                    'device_types': [{'type': dtype, 'energy': energy} for dtype, energy in device_type_energy.items()],
                    'rooms': [{'name': room, 'energy': energy} for room, energy in room_energy.items()]
                }
                
                await statistics_collection.update_one(
                    {'_id': daily_record['_id']},
                    {'$set': update_data}
                )
                print(f"Updated daily statistics for household {household_id}")
            else:
                # Create new daily record
                daily_stats = {
                    'household_id': household_id,
                    'record_type': 'daily',
                    'timestamp': current_time,
                    'date': current_date,
                    'created_at': current_time,
                    'last_updated': current_time,
                    'total_energy': total_energy,
                    'device_types': [{'type': dtype, 'energy': energy} for dtype, energy in device_type_energy.items()],
                    'rooms': [{'name': room, 'energy': energy} for room, energy in room_energy.items()]
                }
                
                await statistics_collection.insert_one(daily_stats)
                print(f"Created daily statistics for household {household_id}")
            
            # Also create/update hourly record for time-series data
            hourly_record = await statistics_collection.find_one({
                'household_id': household_id,
                'date': current_date,
                'hour': current_hour,
                'record_type': 'hourly'
            })
            
            if hourly_record:
                # Update existing hourly record
                await statistics_collection.update_one(
                    {'_id': hourly_record['_id']},
                    {'$set': {
                        'last_updated': current_time,
                        'total_energy': total_energy,
                        'device_types': [{'type': dtype, 'energy': energy} for dtype, energy in device_type_energy.items()],
                        'rooms': [{'name': room, 'energy': energy} for room, energy in room_energy.items()]
                    }}
                )
                print(f"Updated hourly statistics for household {household_id} at hour {current_hour}")
            else:
                # Create new hourly record
                hourly_stats = {
                    'household_id': household_id,
                    'record_type': 'hourly',
                    'timestamp': current_time,
                    'date': current_date,
                    'hour': current_hour,
                    'created_at': current_time,
                    'last_updated': current_time,
                    'total_energy': total_energy,
                    'device_types': [{'type': dtype, 'energy': energy} for dtype, energy in device_type_energy.items()],
                    'rooms': [{'name': room, 'energy': energy} for room, energy in room_energy.items()]
                }
                
                await statistics_collection.insert_one(hourly_stats)
                print(f"Created hourly statistics for household {household_id} at hour {current_hour}")
        
        # Process statistics for each user
        for user_id, devices in user_device_map.items():
            # Skip if this user's devices are already covered by household stats
            household_id = None
            for device in devices:
                if device.get('household_id'):
                    household_id = device.get('household_id')
                    break
            
            if household_id and household_id in household_device_map:
                continue  # Skip as this user's data is already in household stats
            
            # Calculate energy metrics for this user
            total_energy = 0
            device_type_energy = {}
            room_energy = {}
            
            for device in devices:
                device_name = device.get('device_name', device.get('name', 'Unknown Device'))
                device_type = device.get('deviceType', device.get('type', 'unknown'))
                device_room = device.get('room', 'unknown')
                device_status = device.get('status', 'off')
                energy_usage_per_hour = device.get('energy_usage_per_hour', device.get('base_power_consumption', 0))
                last_status_change = device.get('last_status_change')
                total_energy_consumed = device.get('total_energy_consumed', 0)
                
                # Calculate energy for this device
                device_energy = 0
                
                if device_status == 'on' and energy_usage_per_hour > 0:
                    # If device is on, calculate real-time energy consumption
                    if last_status_change:
                        last_change = datetime.fromisoformat(last_status_change.replace('Z', '+00:00')) if isinstance(last_status_change, str) else last_status_change
                        hours_since_on = (current_time - last_change).total_seconds() / 3600
                        device_energy = (energy_usage_per_hour * hours_since_on) / 1000  # Convert to kWh
                    else:
                        # Fallback: assume it's been on for the last hour
                        device_energy = energy_usage_per_hour / 1000
                else:
                    # If device is off, use stored total energy
                    device_energy = total_energy_consumed
                
                # Add to totals
                total_energy += device_energy
                
                # Add to device type map
                if device_type not in device_type_energy:
                    device_type_energy[device_type] = 0
                device_type_energy[device_type] += device_energy
                
                # Add to room map
                if device_room not in room_energy:
                    room_energy[device_room] = 0
                room_energy[device_room] += device_energy
            
            # Check if a daily record already exists for this user
            daily_record = await statistics_collection.find_one({
                'user_id': user_id,
                'date': current_date,
                'record_type': 'daily'
            })
            
            if daily_record:
                # Update existing daily record
                update_data = {
                    'last_updated': current_time,
                    'total_energy': total_energy,  # Replace with current total
                    'device_types': [{'type': dtype, 'energy': energy} for dtype, energy in device_type_energy.items()],
                    'rooms': [{'name': room, 'energy': energy} for room, energy in room_energy.items()]
                }
                
                await statistics_collection.update_one(
                    {'_id': daily_record['_id']},
                    {'$set': update_data}
                )
                print(f"Updated daily statistics for user {user_id}")
            else:
                # Create new daily record
                daily_stats = {
                    'user_id': user_id,
                    'record_type': 'daily',
                    'timestamp': current_time,
                    'date': current_date,
                    'created_at': current_time,
                    'last_updated': current_time,
                    'total_energy': total_energy,
                    'device_types': [{'type': dtype, 'energy': energy} for dtype, energy in device_type_energy.items()],
                    'rooms': [{'name': room, 'energy': energy} for room, energy in room_energy.items()]
                }
                
                await statistics_collection.insert_one(daily_stats)
                print(f"Created daily statistics for user {user_id}")
                
            # Also create/update hourly record for time-series data
            hourly_record = await statistics_collection.find_one({
                'user_id': user_id,
                'date': current_date,
                'hour': current_hour,
                'record_type': 'hourly'
            })
            
            if hourly_record:
                # Update existing hourly record
                await statistics_collection.update_one(
                    {'_id': hourly_record['_id']},
                    {'$set': {
                        'last_updated': current_time,
                        'total_energy': total_energy,
                        'device_types': [{'type': dtype, 'energy': energy} for dtype, energy in device_type_energy.items()],
                        'rooms': [{'name': room, 'energy': energy} for room, energy in room_energy.items()]
                    }}
                )
                print(f"Updated hourly statistics for user {user_id} at hour {current_hour}")
            else:
                # Create new hourly record
                hourly_stats = {
                    'user_id': user_id,
                    'record_type': 'hourly',
                    'timestamp': current_time,
                    'date': current_date,
                    'hour': current_hour,
                    'created_at': current_time,
                    'last_updated': current_time,
                    'total_energy': total_energy,
                    'device_types': [{'type': dtype, 'energy': energy} for dtype, energy in device_type_energy.items()],
                    'rooms': [{'name': room, 'energy': energy} for room, energy in room_energy.items()]
                }
                
                await statistics_collection.insert_one(hourly_stats)
                print(f"Created hourly statistics for user {user_id} at hour {current_hour}")
            
    except Exception as e:
        print(f"Error collecting statistics: {str(e)}")

# Background task that runs collect_statistics every minute
async def collect_statistics_periodically():
    while True:
        await collect_statistics()
        await asyncio.sleep(60)  # Run every 60 seconds

@app.get("/api/statistics")
async def get_statistics(timeRange: str = "week", userId: str = None, householdId: str = None):
    try:
        print(f"Statistics API request: timeRange={timeRange}, userId={userId}, householdId={householdId}")
        
        if not userId and not householdId:
            raise HTTPException(
                status_code=400,
                detail={"message": "Either userId or householdId must be provided"}
            )
        
        # Determine the time window based on timeRange
        now = datetime.now()
        start_date = now
        
        if timeRange == "day":
            start_date = now - timedelta(days=1)
            # For day view, use hourly records
            record_type = "hourly"
        elif timeRange == "week":
            start_date = now - timedelta(days=7)
            # For week view, we could use daily records, but hourly gives better resolution
            record_type = "hourly"
        elif timeRange == "month":
            start_date = now - timedelta(days=30)
            # For month view, daily records are sufficient
            record_type = "daily"
        elif timeRange == "year":
            start_date = now - timedelta(days=365)
            # For year view, daily records are sufficient
            record_type = "daily"
        else:
            # Default to week
            start_date = now - timedelta(days=7)
            record_type = "hourly"
        
        print(f"Using record_type: {record_type}, time range: {start_date} to {now}")
        
        # Build the query for statistics collection
        query = {
            'timestamp': {'$gte': start_date},
            'record_type': record_type
        }
        
        if householdId:
            query['household_id'] = householdId
        elif userId:
            query['user_id'] = userId
            
        print(f"Statistics query: {query}")
        
        # Fetch statistics from collection
        stats_records = await statistics_collection.find(query).sort('timestamp', 1).to_list(length=None)
        
        print(f"Found {len(stats_records)} statistics records")
        
        if not stats_records:
            print(f"No statistics records found for the given parameters")
            
            # As a fallback, try to get the most recent statistics regardless of date range
            fallback_query = {}
            if householdId:
                fallback_query['household_id'] = householdId
            elif userId:
                fallback_query['user_id'] = userId
                
            fallback_records = await statistics_collection.find(fallback_query).sort('timestamp', -1).limit(1).to_list(length=None)
            
            if fallback_records:
                print(f"Using fallback: found 1 recent record")
                stats_records = fallback_records
            else:
                print("No historical records found, generating sample data")
                return generate_sample_statistics(timeRange, userId, householdId)
                
        # Process the statistics records
        energy_data = []
        device_type_map = {}
        room_map = {}
        
        # For time series data, maintain original structure
        # We'll aggregate device types and rooms across all records
        for record in stats_records:
            # Add timestamp to energy data
            energy_data.append({
                'timestamp': record['timestamp'].isoformat(),
                'value': record['total_energy']
            })
            
            # Process device types
            for device_type in record.get('device_types', []):
                device_type_name = device_type['type']
                device_energy = device_type['energy']
                
                if device_type_name not in device_type_map:
                    device_type_map[device_type_name] = 0
                device_type_map[device_type_name] += device_energy
            
            # Process rooms
            for room in record.get('rooms', []):
                room_name = room['name']
                room_energy = room['energy']
                
                if room_name not in room_map:
                    room_map[room_name] = 0
                room_map[room_name] += room_energy
        
        # For total energy consumed, we need to be careful not to double-count
        # If we're using hourly records, we'll sum them up
        # If we're using daily records, we'll take the latest value from the most recent day
        total_energy_consumed = 0
        
        if record_type == "hourly":
            # For hourly records, we sum the values for the correct time period
            for record in stats_records:
                total_energy_consumed += record['total_energy']
        else:
            # For daily records, use the latest record's total
            if stats_records:
                # Sort by timestamp descending to get the most recent record
                latest_record = max(stats_records, key=lambda x: x['timestamp'])
                total_energy_consumed = latest_record['total_energy']
        
        # Format device type data
        device_type_data = []
        for dtype, consumption in device_type_map.items():
            device_type_data.append({
                'type': dtype,
                'consumption': consumption,
                'percentage': (consumption / total_energy_consumed * 100) if total_energy_consumed > 0 else 0
            })
        
        # Format room data
        room_data = []
        for room_name, consumption in room_map.items():
            room_data.append({
                'name': room_name,
                'consumption': consumption,
                'percentage': (consumption / total_energy_consumed * 100) if total_energy_consumed > 0 else 0
            })
        
        # Calculate total cost (AED)
        energy_rate = 0.45  # AED per kWh
        total_cost = total_energy_consumed * energy_rate
        
        # Determine most active room
        most_active_room = {"name": "None", "consumption": 0}
        if room_data:
            most_active_room_data = max(room_data, key=lambda x: x['consumption'])
            most_active_room = {
                "name": most_active_room_data['name'],
                "consumption": most_active_room_data['consumption']
            }
        
        # Calculate a realistic energy savings value (for demo purposes)
        # In a real app, this would compare to historical averages
        energy_savings = 10 if total_energy_consumed > 0 else 0
        
        # Return formatted statistics
        return {
            "energyData": energy_data,
            "deviceTypeData": device_type_data,
            "roomData": room_data,
            "totalEnergyConsumed": total_energy_consumed,
            "totalCost": total_cost,
            "mostActiveRoom": most_active_room,
            "energySavings": energy_savings
        }
        
    except Exception as e:
        print(f"Error retrieving statistics: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail={"message": "Internal server error", "error": str(e)}
        )

# Function to generate sample statistics data for testing
def generate_sample_statistics(timeRange: str, userId: str = None, householdId: str = None):
    print(f"Generating sample statistics for timeRange={timeRange}")
    now = datetime.now()
    start_date = now
    
    # Set date ranges based on timeRange
    if timeRange == "day":
        start_date = now - timedelta(days=1)
        intervals = 24  # 24 hours
        interval_seconds = 60 * 60  # 1 hour
    elif timeRange == "week":
        start_date = now - timedelta(days=7)
        intervals = 7  # 7 days
        interval_seconds = 24 * 60 * 60  # 1 day
    elif timeRange == "month":
        start_date = now - timedelta(days=30)
        intervals = 30  # 30 days
        interval_seconds = 24 * 60 * 60  # 1 day
    elif timeRange == "year":
        start_date = now - timedelta(days=365)
        intervals = 12  # 12 months
        interval_seconds = 30 * 24 * 60 * 60  # ~30 days
    else:
        # Default to week
        start_date = now - timedelta(days=7)
        intervals = 7
        interval_seconds = 24 * 60 * 60

    # Generate time series energy data
    energy_data = []
    total_energy = 0
    
    # Create a realistic usage pattern with random variation
    base_consumption = 2.5  # Base consumption in kWh
    
    for i in range(intervals):
        # Calculate timestamp for this interval
        interval_time = start_date + timedelta(seconds=i * interval_seconds)
        
        # Add random variation to consumption
        # Higher during day (8am-10pm), lower at night
        hour = interval_time.hour
        day_multiplier = 1.5 if 8 <= hour <= 22 else 0.6
        
        # Add some randomness
        random_factor = 0.8 + (random.random() * 0.4)  # 0.8 to 1.2
        
        # Calculate energy value for this interval
        energy_value = base_consumption * day_multiplier * random_factor
        total_energy += energy_value
        
        # Add to energy data
        energy_data.append({
            'timestamp': interval_time.isoformat(),
            'value': energy_value
        })
    
    # Generate device type data
    device_types = ["lightbulb", "tv", "ac", "fridge", "computer"]
    device_type_data = []
    
    # Distribute total energy among device types
    remaining_energy = total_energy
    for i, device_type in enumerate(device_types):
        # Last device gets remaining energy
        if i == len(device_types) - 1:
            consumption = remaining_energy
        else:
            # Random percentage of remaining energy
            percentage = 0.1 + (random.random() * 0.3)  # 10% to 40%
            consumption = remaining_energy * percentage
            remaining_energy -= consumption
        
        device_type_data.append({
            'type': device_type,
            'consumption': consumption,
            'percentage': (consumption / total_energy * 100) if total_energy > 0 else 0
        })
    
    # Generate room data
    rooms = ["Living Room", "Kitchen", "Bedroom", "Bathroom", "Office"]
    room_data = []
    
    # Distribute total energy among rooms
    remaining_energy = total_energy
    for i, room in enumerate(rooms):
        # Last room gets remaining energy
        if i == len(rooms) - 1:
            consumption = remaining_energy
        else:
            # Random percentage of remaining energy
            percentage = 0.1 + (random.random() * 0.3)  # 10% to 40%
            consumption = remaining_energy * percentage
            remaining_energy -= consumption
        
        room_data.append({
            'name': room,
            'consumption': consumption,
            'percentage': (consumption / total_energy * 100) if total_energy > 0 else 0
        })
    
    # Determine most active room
    most_active_room = max(room_data, key=lambda x: x['consumption'])
    
    # Calculate total cost
    energy_rate = 0.45  # AED per kWh
    total_cost = total_energy * energy_rate
    
    # Mock energy savings (10%)
    energy_savings = 10
    
    return {
        "energyData": energy_data,
        "deviceTypeData": device_type_data,
        "roomData": room_data,
        "totalEnergyConsumed": total_energy,
        "totalCost": total_cost,
        "mostActiveRoom": {
            "name": most_active_room['name'],
            "consumption": most_active_room['consumption']
        },
        "energySavings": energy_savings
    }

@app.get("/api/automations/active")
async def get_active_automations(user_id: str, household_id: str = None, timestamp: str = None):
    try:
        # Parse the timestamp
        current_time = datetime.fromisoformat(timestamp.replace('Z', '+00:00')) if timestamp else datetime.now()
        
        # Find all active automations for this user/household
        query = {
            'user_id': user_id,
            'active': True
        }
        if household_id:
            query['household_id'] = household_id
            
        automations = await db.automations.find(query).to_list(length=100)
        
        # Check which automations should be active right now
        active_automations = []
        
        for automation in automations:
            try:
                schedule = automation["schedule"]
                start_time = parse_time(schedule["startTime"])
                end_time = parse_time(schedule["endTime"])
                
                # Determine if the automation should be active now
                should_be_active = False
                current_time_only = current_time.time()
                
                # Check schedule type
                if schedule["type"] == "once":
                    # For "once" type, check if current time is between start and end
                    should_be_active = start_time <= current_time_only <= end_time
                    
                elif schedule["type"] == "daily":
                    # For "daily" type, check if current time is between start and end
                    
                    # Handle overnight schedules (end time is less than start time)
                    if end_time < start_time:
                        should_be_active = current_time_only >= start_time or current_time_only <= end_time
                    else:
                        should_be_active = start_time <= current_time_only <= end_time
                        
                elif schedule["type"] == "weekly" and schedule.get("daysOfWeek"):
                    # For "weekly" type, check if today is in the days of week and time is between start and end
                    current_weekday = current_time.weekday()
                    
                    # Convert daysOfWeek to integers if they're strings
                    days_of_week = [int(day) if isinstance(day, str) else day for day in schedule["daysOfWeek"]]
                    
                    if current_weekday in days_of_week:
                        # Handle overnight schedules
                        if end_time < start_time:
                            should_be_active = current_time_only >= start_time or current_time_only <= end_time
                        else:
                            should_be_active = start_time <= current_time_only <= end_time
                
                if should_be_active:
                    # Check if we've already recorded this activation
                    activation_record = await db.automation_activations.find_one({
                        'automation_id': str(automation["_id"]),
                        'date': current_time.date().isoformat()
                    })
                    
                    # If no activation record for today, create one
                    if not activation_record:
                        await db.automation_activations.insert_one({
                            'automation_id': str(automation["_id"]),
                            'date': current_time.date().isoformat(),
                            'activated_at': current_time,
                            'devices': automation["devices"]
                        })
                        
                        # Also update the automation with last_activated timestamp
                        await db.automations.update_one(
                            {'_id': automation["_id"]},
                            {'$set': {'last_activated': current_time}}
                        )
                        
                        # Toggle the devices
                        for device_id in automation["devices"]:
                            await toggle_device(user_id, device_id, household_id, "on")
                    
                    # Add to active automations list
                    automation_copy = dict(automation)
                    automation_copy["_id"] = str(automation["_id"])
                    automation_copy["last_activated"] = activation_record["activated_at"] if activation_record else current_time
                    active_automations.append(automation_copy)
            
            except Exception as e:
                print(f"Error processing automation {automation.get('_id', 'unknown')}: {str(e)}")
                continue
        
        return {
            "active_automations": active_automations,
            "timestamp": current_time.isoformat()
        }
    
    except Exception as e:
        print(f"Error checking active automations: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail={"message": "Internal server error", "error": str(e)}
        )

@app.post("/api/statistics/collect")
async def force_collect_statistics(user_id: Optional[str] = None, household_id: Optional[str] = None):
    try:
        print(f"Force collecting statistics for user_id={user_id}, household_id={household_id}")
        
        # Force run the statistics collection
        await collect_statistics()
        
        return {"message": "Statistics collection triggered successfully"}
    except Exception as e:
        print(f"Error triggering statistics collection: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail={"message": "Internal server error", "error": str(e)}
        )

# Create an appropriate directory for report storage
REPORTS_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "generated_reports")
os.makedirs(REPORTS_DIR, exist_ok=True)

# Report-related schemas
class ReportFormat(str, Enum):
    PDF = "pdf"
    CSV = "csv"

class ReportCreateRequest(BaseModel):
    title: str
    format: ReportFormat
    start_date: Optional[str] = None
    end_date: Optional[str] = None
    device_ids: Optional[List[str]] = None

# Report endpoints
@app.post("/api/reports/create")
async def create_report(report_data: ReportCreateRequest, background_tasks: BackgroundTasks, user_id: str):
    try:
        # Generate a UUID for the report
        report_id = str(uuid.uuid4())
        
        # Create the report record
        now = datetime.utcnow()
        report = {
            "id": report_id,
            "user_id": user_id,
            "title": report_data.title,
            "format": report_data.format,
            "start_date": report_data.start_date,
            "end_date": report_data.end_date,
            "device_ids": report_data.device_ids or [],
            "status": "pending",
            "created": now,
            "updated": now
        }
        
        # Insert into database
        await reports_collection.insert_one(report)
        
        # Generate the report in background
        background_tasks.add_task(generate_report, report_id)
        
        return {
            "message": "Report generation started",
            "report_id": report_id,
            "status": "pending"
        }
        
    except Exception as e:
        print(f"Error creating report: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail={"message": "Failed to create report", "error": str(e)}
        )

@app.get("/api/reports")
async def list_reports(user_id: str):
    try:
        reports = await reports_collection.find(
            {"user_id": user_id}
        ).sort("created", -1).to_list(length=100)
        
        # Format for response
        formatted_reports = []
        for report in reports:
            formatted_reports.append({
                "id": report["id"],
                "title": report["title"],
                "format": report["format"],
                "status": report["status"],
                "created": report["created"].isoformat() if isinstance(report["created"], datetime) else report["created"],
                "completed": report.get("completed", "").isoformat() if isinstance(report.get("completed"), datetime) else report.get("completed", ""),
                "file_path": report.get("file_path", "")
            })
            
        return formatted_reports
        
    except Exception as e:
        print(f"Error listing reports: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail={"message": "Failed to list reports", "error": str(e)}
        )

@app.get("/api/reports/{report_id}")
async def get_report(report_id: str):
    try:
        report = await reports_collection.find_one({"id": report_id})
        
        if not report:
            raise HTTPException(status_code=404, detail="Report not found")
        
        return {
            "id": report["id"],
            "title": report["title"],
            "format": report["format"],
            "status": report["status"],
            "created": report["created"].isoformat() if isinstance(report["created"], datetime) else report["created"],
            "completed": report.get("completed", "").isoformat() if isinstance(report.get("completed"), datetime) else report.get("completed", ""),
            "file_path": report.get("file_path", ""),
            "error_message": report.get("error_message", "")
        }
        
    except HTTPException:
        raise
    except Exception as e:
        print(f"Error getting report: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail={"message": "Failed to get report", "error": str(e)}
        )

@app.get("/api/reports/{report_id}/download")
async def download_report(report_id: str):
    try:
        report = await reports_collection.find_one({"id": report_id})
        
        if not report:
            raise HTTPException(status_code=404, detail="Report not found")
        
        if report["status"] != "completed":
            raise HTTPException(status_code=400, detail=f"Report not ready. Status: {report['status']}")
        
        file_path = report.get("file_path")
        if not file_path or not os.path.exists(file_path):
            raise HTTPException(status_code=404, detail="Report file not found")
        
        # Determine content type based on format
        content_type = "application/pdf" if report["format"] == "pdf" else "text/csv"
        
        # Return the file as a response
        return FileResponse(
            path=file_path,
            filename=os.path.basename(file_path),
            media_type=content_type
        )
        
    except HTTPException:
        raise
    except Exception as e:
        print(f"Error downloading report: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail={"message": "Failed to download report", "error": str(e)}
        )

# Report generation function
async def generate_report(report_id: str):
    try:
        # Get report data
        report = await reports_collection.find_one({"id": report_id})
        if not report:
            print(f"Report {report_id} not found")
            return
        
        # Update status to generating
        await reports_collection.update_one(
            {"id": report_id},
            {"$set": {"status": "generating", "updated": datetime.utcnow()}}
        )
        
        # Fetch energy data for the specified date range
        start_date = None
        end_date = None
        
        if report.get("start_date"):
            start_date = datetime.strptime(report["start_date"], "%Y-%m-%d")
        if report.get("end_date"):
            end_date = datetime.strptime(report["end_date"], "%Y-%m-%d") + timedelta(days=1) - timedelta(seconds=1)
        
        # Get the user's devices
        device_ids = report.get("device_ids", [])
        if not device_ids:
            # If no device IDs are specified, get all devices for the user
            user_devices = await user_devices_collection.find(
                {"user_id": report["user_id"]}
            ).to_list(length=100)
            device_ids = [device["device_name"] for device in user_devices]
        
        # Query for energy usage data
        query = {}
        
        # Filter by devices if specified
        if device_ids:
            # Loop through device_types array to find matching devices
            query["$or"] = [
                {"device_types.type": {"$in": device_ids}},
                {"devices": {"$in": device_ids}} 
            ]
        
        # Filter by user or household
        if ObjectId.is_valid(report["user_id"]):
            # It's likely an admin user ID
            admin_user = await admin_users_collection.find_one({"_id": ObjectId(report["user_id"])})
            if admin_user and admin_user.get("household_id"):
                query["household_id"] = admin_user["household_id"]
        else:
            # It might be a household member
            query["user_id"] = report["user_id"]
        
        # Add date range filter
        if start_date or end_date:
            date_filter = {}
            if start_date:
                date_filter["$gte"] = start_date
            if end_date:
                date_filter["$lte"] = end_date
                
            if date_filter:
                query["timestamp"] = date_filter
        
        # Fetch statistics records
        records = await statistics_collection.find(query).sort("timestamp", 1).to_list(length=1000)
        
        if not records:
            # No data found, create sample data
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
            return
        
        # Process data for the report generator
        energy_data = []
        for record in records:
            # Process device types from the record
            if "device_types" in record:
                for device_type in record["device_types"]:
                    energy_data.append({
                        "timestamp": record.get("timestamp"),
                        "device_id": device_type["type"],
                        "energy_consumed": device_type["energy"],
                        "location": record.get("room", "Unknown")
                    })
            else:
                # Fallback for records without device_types
                energy_data.append({
                    "timestamp": record.get("timestamp"),
                    "device_id": "Unknown",
                    "energy_consumed": record.get("total_energy", 0),
                    "location": record.get("room", "Unknown")
                })
        
        # Get user data for personalization
        user_data = {}
        if ObjectId.is_valid(report["user_id"]):
            admin_user = await admin_users_collection.find_one({"_id": ObjectId(report["user_id"])})
            if admin_user:
                user_data = {
                    "email": admin_user.get("admin_email"),
                    "username": f"{admin_user.get('firstName', '')} {admin_user.get('lastName', '')}"
                }
        else:
            # Might be a household member
            member = await household_members_collection.find_one({"email": report["user_id"]})
            if member:
                user_data = {
                    "email": member.get("email"),
                    "username": member.get("name")
                }
        
        # Create the report file
        # Note: You'll need to import and implement the report_generator functionality
        from report_generator import generate_energy_report
        
        report_path = generate_energy_report(
            energy_data=energy_data,
            user_data=user_data,
            format=report["format"].lower(),
            start_date=report.get("start_date"),
            end_date=report.get("end_date")
        )
        
        if not report_path:
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
            return
        
        # Update report record with success
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
        
        print(f"Report {report_id} generated successfully: {report_path}")
        
    except Exception as e:
        print(f"Error generating report {report_id}: {str(e)}")
        # Update report record with failure
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

# Create a simple wrapper function for the existing energy report generator
def generate_energy_report(energy_data, user_data=None, format="pdf", start_date=None, end_date=None):
    try:
        # Generate report filename
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"{REPORTS_DIR}/energy_report_{timestamp}.{format}"
        
        # Create a basic report
        if format.lower() == "csv":
            # Generate CSV report
            with open(filename, 'w') as f:
                # Write header
                f.write("Timestamp,Device,Energy Consumed (kWh),Location\n")
                
                # Write data rows
                for item in energy_data:
                    timestamp = item.get('timestamp', '')
                    if isinstance(timestamp, datetime):
                        timestamp = timestamp.strftime("%Y-%m-%d %H:%M:%S")
                    
                    f.write(f"{timestamp},{item.get('device_id', 'Unknown')},{item.get('energy_consumed', 0)},{item.get('location', 'Unknown')}\n")
        else:
            # Generate PDF report (requires reportlab)
            from reportlab.lib.pagesizes import letter
            from reportlab.lib.styles import getSampleStyleSheet
            from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
            from reportlab.lib import colors
            
            doc = SimpleDocTemplate(filename, pagesize=letter)
            styles = getSampleStyleSheet()
            
            elements = []
            
            # Title
            title = "Sync Energy Consumption Report"
            if start_date and end_date:
                title += f" ({start_date} to {end_date})"
            elements.append(Paragraph(title, styles['Title']))
            elements.append(Spacer(1, 12))
            
            # User info
            if user_data and user_data.get('email'):
                elements.append(Paragraph(f"Report for: {user_data.get('email')}", styles['Normal']))
            
            elements.append(Paragraph(f"Generated on: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}", styles['Normal']))
            elements.append(Spacer(1, 12))
            
            # Summary
            elements.append(Paragraph("Summary", styles['Heading2']))
            
            # Calculate total energy and group by device
            total_energy = sum(item.get('energy_consumed', 0) for item in energy_data)
            
            # Group by device
            devices = {}
            for item in energy_data:
                device_id = item.get('device_id', 'Unknown')
                energy = item.get('energy_consumed', 0)
                
                if device_id not in devices:
                    devices[device_id] = 0
                devices[device_id] += energy
            
            # Create summary table
            summary_data = [['Metric', 'Value']]
            summary_data.append(['Total Energy Consumption', f"{total_energy:.2f} kWh"])
            summary_data.append(['Total Estimated Cost', f"{total_energy * 0.45:.2f} AED"])  # Assuming 0.45 AED per kWh
            
            if start_date and end_date:
                summary_data.append(['Date Range', f"{start_date} to {end_date}"])
            
            summary_table = Table(summary_data, colWidths=[200, 200])
            summary_table.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (1, 0), colors.grey),
                ('TEXTCOLOR', (0, 0), (1, 0), colors.whitesmoke),
                ('ALIGN', (0, 0), (1, 0), 'CENTER'),
                ('FONTNAME', (0, 0), (1, 0), 'Helvetica-Bold'),
                ('FONTSIZE', (0, 0), (1, 0), 14),
                ('BOTTOMPADDING', (0, 0), (1, 0), 12),
                ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
                ('BOX', (0, 0), (-1, -1), 1, colors.black),
                ('GRID', (0, 0), (-1, -1), 1, colors.black)
            ]))
            
            elements.append(summary_table)
            elements.append(Spacer(1, 12))
            
            # Device breakdown
            elements.append(Paragraph("Device Breakdown", styles['Heading2']))
            
            device_data = [['Device', 'Energy (kWh)', 'Percentage', 'Cost (AED)']]
            for device, energy in sorted(devices.items(), key=lambda x: x[1], reverse=True):
                percentage = (energy / total_energy * 100) if total_energy > 0 else 0
                cost = energy * 0.45  # Assuming 0.45 AED per kWh
                device_data.append([device, f"{energy:.2f}", f"{percentage:.1f}%", f"{cost:.2f}"])
            
            device_table = Table(device_data, colWidths=[120, 100, 100, 100])
            device_table.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
                ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
                ('ALIGN', (0, 0), (-1, 0), 'CENTER'),
                ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                ('FONTSIZE', (0, 0), (-1, 0), 12),
                ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
                ('BACKGROUND', (0, 1), (-1, -1), colors.white),
                ('BOX', (0, 0), (-1, -1), 1, colors.black),
                ('GRID', (0, 0), (-1, -1), 1, colors.black),
                ('ALIGN', (1, 1), (-1, -1), 'RIGHT')
            ]))
            
            elements.append(device_table)
            elements.append(Spacer(1, 12))
            
            # Recommendations
            elements.append(Paragraph("Energy Saving Recommendations", styles['Heading2']))
            
            tips = [
                "Use LED bulbs instead of traditional incandescent bulbs to save up to 80% on lighting energy.",
                "Set your thermostat to 24°C (75°F) in summer and 20°C (68°F) in winter to optimize energy use.",
                "Unplug electronics and appliances when not in use to eliminate phantom power usage.",
                "Consider installing smart power strips that cut power to devices when they're not in use.",
                "Use natural light when possible and turn off lights when leaving a room."
            ]
            
            for tip in tips:
                elements.append(Paragraph(f"• {tip}", styles['Normal']))
                elements.append(Spacer(1, 6))
            
            # Build the PDF
            doc.build(elements)
            
        # Return the path to the generated file
        return filename
        
    except Exception as e:
        print(f"Error in basic report generation: {str(e)}")
        return None

