from fastapi import FastAPI, HTTPException, Body, Depends
from motor.motor_asyncio import AsyncIOMotorClient
from passlib.context import CryptContext
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import random
import datetime
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from bson import ObjectId

# Initialize FastAPI
app = FastAPI()

# Database connection
client = AsyncIOMotorClient("mongodb://localhost:27017")
db = client.project_test
devices_collection = db['devices']
user_devices_collection = db['user_devices']  # New collection to link users and devices
permissions_collection = db['permissions']  # New collection for permissions
admin_users_collection = db['admin_users']
household_members_collection = db['household_members']

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
                    <img src="https://your-app-logo-url.com/logo.png" alt="SYNC Logo" style="width: 120px; margin-bottom: 20px;">
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
    expires_at = datetime.datetime.utcnow() + datetime.timedelta(minutes=5)

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
    if datetime.datetime.utcnow() > user.get("otp_expires_at"):
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
    expires_at = datetime.datetime.utcnow() + datetime.timedelta(minutes=5)
    await db.admin_users.update_one({"admin_email": admin_email}, {"$set": {"otp": otp, "otp_expires_at": expires_at}})
    send_email(admin_email, otp)

    return {"msg": "OTP sent to your email"}

# Forgot Password - Verify OTP
@app.post("/verify-forgot-password-otp")
async def verify_forgot_password_otp(data: OTPVerify):
    admin_email, otp = data.email, data.otp
    user = await db.admin_users.find_one({"admin_email": admin_email})
    if not user or user.get("otp") != otp or user.get("otp_expires_at") < datetime.datetime.utcnow():
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

# Add this endpoint with your existing routes
@app.post("/register_personal")
async def register_personal(data: PersonalDetailsRequest):
    try:
        # Convert birthdate components to date object
        birthdate = datetime.datetime(
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
                "address": data.address
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

class TrackEnergyRequest(BaseModel):
    user_id: str
    device_name: str
    hours: int

# Update endpoints to use request body models
@app.get("/api/user/devices")
async def get_user_devices(user_id: str):
    user_devices = await user_devices_collection.find(
        {'user_id': user_id},
        {'_id': 0, 'user_id': 0}
    ).to_list(length=100)

    transformed_devices = [
        {"name": device["device_name"], "energy_usage_per_hour": device["energy_usage_per_hour"]}
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


@app.post("/api/user/add-device")
async def add_device_to_user(data: AddDeviceRequest):
    try:
        # Check if device exists
        device = await devices_collection.find_one({'name': data.device_name})
        if not device:
            raise HTTPException(
                status_code=404,
                detail={"message": "Device not found", "device": data.device_name}
            )

        # Check for duplicates
        existing = await user_devices_collection.find_one({
            "user_id": data.user_id,
            "device_name": data.device_name
        })
        if existing:
            raise HTTPException(
                status_code=400,
                detail={"message": "Device already added", "device": data.device_name}
            )

        # Insert the device
        await user_devices_collection.insert_one({
            "user_id": data.user_id,
            "device_name": data.device_name,
            "energy_usage_per_hour": device["energy_usage_per_hour"]
        })

        return {"message": "Device added successfully"}

    except HTTPException as he:
        raise he  # Re-raise HTTPExceptions
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail={"message": "Internal server error", "error": str(e)}
        )

@app.get("/api/devices")
async def get_devices(search: str = None):
    query = {}
    if search:
        query = {"name": {"$regex": search, "$options": "i"}}
    devices = await devices_collection.find(query, {'_id': 0}).to_list(length=100)
    return devices

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
async def create_profile(data: CreateProfileRequest):
    name = data.name
    email = data.email
    account_type = data.account_type
    pin_option = data.pin_option
    household_id = data.household_id
    admin_user = data.admin_user
    pin = data.pin # Get the pin
    permissions = data.permissions

    # Add the profile to the household_members collection
    member = {
        "name": name,
        "email": email,
        "account_type": account_type,
        "household_id": household_id,
        "admin_user": admin_user,
        "pin": pin
    }
    await household_members_collection.insert_one(member)


    # Create or update permissions document
    permissions_doc = {
        "household_id": household_id,
        "admin_email": email,
        "permissions": permissions
    }

    await permissions_collection.insert_one(permissions_doc)
    return {"msg": "Profile created successfully"}

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
      return user
    else:
      raise HTTPException(status_code=404, detail="User not found")

@app.get("/api/permissions/{email}")
async def get_permissions(email: str):
    permissions = await get_user_permissions(email)
    if permissions:
        return permissions
    else:
        raise HTTPException(status_code=404, detail="Permissions not found")

@app.get("/api/household-members/{household_id}")
async def get_household_members(household_id: str):
    members = await household_members_collection.find({"household_id": household_id}).to_list(length=100)
    for member in members:
        member["_id"] = str(member["_id"])  # Convert ObjectId to string
    return members

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