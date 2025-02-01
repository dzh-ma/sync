from fastapi import FastAPI, HTTPException, Body
from motor.motor_asyncio import AsyncIOMotorClient
from passlib.context import CryptContext
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import random
import datetime
import smtplib
from email.mime.text import MIMEText
from bson import ObjectId

# Initialize FastAPI
app = FastAPI()

# Database connection
client = AsyncIOMotorClient("mongodb://localhost:27017")
db = client.project_test

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

    msg = MIMEText(f"Your OTP code is {otp}. It is valid for 5 minutes.")
    msg['Subject'] = 'Your OTP Code'
    msg['From'] = from_email
    msg['To'] = to_email

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
    email = data.get("email")
    password = data.get("password")

    # Check if the email is already registered
    user = await db.users.find_one({"email": email})
    if user:
        raise HTTPException(status_code=400, detail="Email already registered")

    # Hash the password and store the user in the database
    hashed_password = get_password_hash(password)
    await db.users.insert_one({"email": email, "password": hashed_password})

    return {"msg": "User registered successfully"}

# OTP request and verification schemas
class OTPRequest(BaseModel):
    email: str

class OTPVerify(BaseModel):
    email: str
    otp: str

# Request OTP API
@app.post("/request-otp")
async def request_otp(data: OTPRequest):
    email = data.email
    otp = generate_otp()
    expires_at = datetime.datetime.utcnow() + datetime.timedelta(minutes=5)

    # Update the user's document with the OTP and expiration
    result = await db.users.update_one(
        {"email": email},
        {"$set": {"otp": otp, "otp_expires_at": expires_at}}
    )

    if result.matched_count == 0:
        raise HTTPException(status_code=404, detail="User not found")

    # Send the OTP email
    send_email(email, otp)
    return {"msg": "OTP sent to your email"}

# Verify OTP API
@app.post("/verify-otp")
async def verify_otp(data: OTPVerify):
    email = data.email
    otp = data.otp

    # Retrieve the user's data
    user = await db.users.find_one({"email": email})

    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    # Check if the OTP matches and is not expired
    if user.get("otp") != otp:
        raise HTTPException(status_code=400, detail="Invalid OTP")
    if datetime.datetime.utcnow() > user.get("otp_expires_at"):
        raise HTTPException(status_code=400, detail="OTP has expired")

    # Clear the OTP after successful verification
    await db.users.update_one(
        {"email": email},
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
    email = data.email
    password = data.password

    # Fetch the user from the database
    user = await db.users.find_one({"email": email})

    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    # Verify the password
    if not verify_password(password, user["password"]):
        raise HTTPException(status_code=401, detail="Invalid password")

    return {"msg": "Login successful"}

# Reset Password Schema
class ResetPassword(BaseModel):
    email: str
    new_password: str

# Request OTP for password reset
@app.post("/forgot-password/request-otp")
async def forgot_password_request_otp(data: OTPRequest):
    email = data.email
    otp = generate_otp()
    expires_at = datetime.datetime.utcnow() + datetime.timedelta(minutes=5)

    user = await db.users.find_one({"email": email})
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    await db.users.update_one(
        {"email": email},
        {"$set": {"otp": otp, "otp_expires_at": expires_at}}
    )
    send_email(email, otp)
    return {"msg": "OTP sent to your email"}

# Verify OTP for password reset
@app.post("/forgot-password/verify-otp")
async def forgot_password_verify_otp(data: OTPVerify):
    email = data.email
    otp = data.otp

    user = await db.users.find_one({"email": email})
    if not user or user.get("otp") != otp or datetime.datetime.utcnow() > user.get("otp_expires_at"):
        raise HTTPException(status_code=400, detail="Invalid or expired OTP")

    await db.users.update_one(
        {"email": email},
        {"$unset": {"otp": "", "otp_expires_at": ""}}
    )
    return {"msg": "OTP verified successfully", "success": True}

# Reset password after OTP verification
@app.post("/forgot-password/reset-password")
async def reset_password(data: ResetPassword):
    email = data.email
    new_password = data.new_password

    hashed_password = get_password_hash(new_password)
    result = await db.users.update_one(
        {"email": email},
        {"$set": {"password": hashed_password}}
    )

    if result.matched_count == 0:
        raise HTTPException(status_code=404, detail="User not found")

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
        result = await db.users.find_one_and_update(
            {"email": data.email},
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

        # Convert ObjectId to string
        result["_id"] = str(result["_id"])

        return {"msg": "Personal details saved successfully", "user": result}

    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))
