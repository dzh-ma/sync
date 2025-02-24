"""
This module provides email verification functionalities

It handles:
- Loading SMTP credentials from an external configuration file
- Generating time-limited verification tokens
- Confirming & decoding verification tokens
- Sending verification emails to users via SMTP

IMPORTANT:
    Ensure that the configuration file is properly set up and that sensitive credentials remain out of version control.
"""
import os
import smtplib
import configparser
from email.mime.text import MIMEText
from itsdangerous import URLSafeTimedSerializer
from fastapi import HTTPException

# Load credentials from external config file
config = configparser.ConfigParser()
config.read(os.path.join(os.path.dirname(__file__), "email_config.ini"))
SMTP_EMAIL = config.get("smtp", "email")
SMTP_PASSWORD = config.get("smtp", "password")

# Use environment variables or configuration files in production
SECRET_KEY = os.getenv("SECRET_KEY", "mysecretkey")
SECURITY_PASSWORD_SALT = os.getenv("SECURITY_PASSWORD_SALT", "mysalt")

def generate_verification_token(email: str) -> str:
    """
    Generate a time-limited token for verifying an email

    Args:
        email (str): The email address to verify

    Returns:
        str: A secure token
    """
    serializer = URLSafeTimedSerializer(SECRET_KEY)
    token = serializer.dumps(email, salt = SECURITY_PASSWORD_SALT)
    if isinstance(token, bytes):
        token = token.decode("utf-8")
    return token

def confirm_verification_token(token: str, expiration: int = 3600) -> str:
    """
    Confirm & decode a verification token

    Args:
        token (str): The token to decode
        expiration (int): Token expiration time in seconds (defaults to 3600 seconds)

    Returns:
        str: The email address contained in the token

    Raises:
        HTTPException: If the token is invalid or expired
    """
    serializer = URLSafeTimedSerializer(SECRET_KEY)
    try:
        email = serializer.loads(token, salt = SECURITY_PASSWORD_SALT, max_age = expiration)
    except Exception as exc:
        raise HTTPException(status_code = 400, detail = "Verification link is invalid or expired.") from exc
    return email

def send_verification_email(email: str, token: str):
    """
    Sends a verification email containing a link with the verification token

    Args:
        email (str): The recipient's email address
        token (str): The verification token to include in the link
    """
    verification_link = f"http://127.0.0.1:8000/api/v1/users/verify?token={token}"
    subject = "Verify your email for the Sync Smart Home"
    body = f"Please click the following link to verify your email:\n\n{verification_link}"

    msg = MIMEText(body)
    msg["Subject"] = subject
    msg["From"] = SMTP_EMAIL
    msg["To"] = email

    try:
        # Example using Gmail SMPTP; update credentials as needed
        with smtplib.SMTP("smtp.gmail.com", 587) as server:
            server.starttls()
            server.login(SMTP_EMAIL, SMTP_PASSWORD)
            server.send_message(msg)
    except Exception as exc:
        # In production, log this error appropriately
        print("Error sending email:", exc)
