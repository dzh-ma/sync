"""
Database seeding script for Smart Home Automation platform.
This script populates the MongoDB collections with realistic data.
"""
import os
import sys
import uuid
import random
import datetime
import hashlib
import json
from typing import Dict, List, Any, Optional, Tuple
from datetime import datetime, timedelta
from passlib.context import CryptContext

pc = CryptContext(schemes=["bcrypt"], deprecated="auto")

# Try to import pymongo and faker, install if not available
try:
    from pymongo import MongoClient
    from faker import Faker
except ImportError:
    print("Installing required packages...")
    os.system("pip install pymongo faker")
    from pymongo import MongoClient
    from faker import Faker

# Initialize Faker
fake = Faker()
Faker.seed(42)  # For reproducibility

# Connect to MongoDB
MONGO_URI = os.getenv("MONGO_URI", "mongodb://localhost:27017/")
try:
    client = MongoClient(MONGO_URI)
    db = client.sync

    # Get collections
    user_collection = db["user"]
    profile_collection = db["profile"]
    device_collection = db["device"]
    room_collection = db["room"]
    usage_collection = db["usage"]
    automation_collection = db["automation"]
    notification_collection = db["notification"]
    access_management_collection = db["access management"]
    goal_collection = db["goal"]
    analytics_collection = db["analytics"]
    suggestion_collection = db["suggestion"]

    print(f"Connected to MongoDB database: {MONGO_URI}")
except Exception as e:
    sys.exit(f"Failed to connect to MongoDB: {e}")

# Clear existing data
def clear_collections():
    """Clear all collections to start fresh."""
    collections = [
        user_collection, profile_collection, device_collection, room_collection, 
        usage_collection, automation_collection, notification_collection, 
        access_management_collection, goal_collection, analytics_collection, 
        suggestion_collection
    ]
    for collection in collections:
        collection.delete_many({})
    print("All collections cleared.")

# Helper functions
def generate_uuid() -> str:
    """Generate a UUID string."""
    return str(uuid.uuid4())

def hash_password(password: str) -> str:
    """Create a hashed password."""
    # return hashlib.sha256(password.encode()).hexdigest()
    return pc.hash(password)

def random_date(start_date: datetime, end_date: datetime) -> datetime:
    """Generate a random date between start_date and end_date."""
    if start_date >= end_date:
        return start_date  # Return start_date if range is invalid
    delta = end_date - start_date
    random_days = random.randrange(delta.days + 1)  # Add 1 to include end_date
    return start_date + timedelta(days=random_days)

def random_datetime(start_date: datetime, end_date: datetime) -> datetime:
    """Generate a random datetime between start_date and end_date."""
    if start_date >= end_date:
        return start_date  # Return start_date if range is invalid
    delta = end_date - start_date
    random_seconds = random.randrange(int(delta.total_seconds()) + 1)  # Add 1 to include end_date
    return start_date + timedelta(seconds=random_seconds)

# Define room types and device types for realistic data
ROOM_TYPES = [
    "Living Room", "Kitchen", "Master Bedroom", "Bedroom", "Bathroom", "Office",
    "Dining Room", "Hallway", "Garage", "Basement", "Attic", "Guest Room",
    "Laundry Room", "Gym", "Home Theater", "Study", "Nursery", "Playroom"
]

DEVICE_CAPABILITIES = {
    "light": ["on/off", "dimming", "color", "scheduling"],
    "thermostat": ["temperature", "scheduling", "eco mode", "remote control"],
    "lock": ["remote locking", "access codes", "history", "notifications"],
    "camera": ["live view", "recording", "motion detection", "night vision"],
    "sensor": ["motion detection", "temperature sensing", "humidity sensing", "open/close detection"],
    "switch": ["on/off", "scheduling", "energy monitoring"],
    "outlet": ["on/off", "energy monitoring", "scheduling"],
    "speaker": ["voice control", "music streaming", "multi-room audio", "intercom"]
}

DEVICE_MANUFACTURERS = {
    "light": ["Philips Hue", "LIFX", "Nanoleaf", "GE", "Sylvania", "TP-Link Kasa"],
    "thermostat": ["Nest", "Ecobee", "Honeywell", "Emerson", "Wyze"],
    "lock": ["August", "Schlage", "Yale", "Kwikset", "Ultraloq"],
    "camera": ["Ring", "Nest", "Arlo", "Wyze", "Eufy", "Blink"],
    "sensor": ["Samsung SmartThings", "Aqara", "Wyze", "Eve", "Philips Hue"],
    "switch": ["Lutron Caseta", "Wemo", "TP-Link Kasa", "GE", "Leviton"],
    "outlet": ["TP-Link Kasa", "Wemo", "Amazon Smart Plug", "Wyze", "Eve Energy"],
    "speaker": ["Amazon Echo", "Google Nest", "Apple HomePod", "Sonos", "Bose"]
}

DEVICE_MODELS = {
    "Philips Hue": ["White and Color Ambiance", "White Ambiance", "Bloom", "Lightstrip Plus", "Play"],
    "Nest": ["Learning Thermostat", "Thermostat E", "Cam IQ", "Hello", "Protect"],
    "August": ["Smart Lock Pro", "Wi-Fi Smart Lock", "Smart Lock", "Doorbell Cam Pro"],
    "Ring": ["Video Doorbell Pro", "Video Doorbell 3", "Stick Up Cam", "Indoor Cam", "Floodlight Cam"],
    "Samsung SmartThings": ["Motion Sensor", "Multipurpose Sensor", "Water Leak Sensor", "Button", "Outlet"],
    "Amazon Echo": ["Dot", "Plus", "Show", "Studio", "Flex", "Auto"]
}

# Create users
def create_users(count: int = 25) -> List[Dict[str, Any]]:
    """Create realistic user data."""
    users = []
    for _ in range(count):
        first_name = fake.first_name()
        last_name = fake.last_name()
        username = f"{first_name.lower()}.{last_name.lower()}{random.randint(1, 999)}"
        email = f"{username}@{fake.domain_name()}"
        
        # Create a strong password that meets requirements
        password = fake.password(length=12) + "A1!"
        
        user_id = generate_uuid()
        user = {
            "id": user_id,
            "username": username,
            "email": email,
            "hashed_password": hash_password(password),
            "active": True,
            "verified": random.random() > 0.1,  # 90% are verified
            "created": random_date(datetime(2023, 1, 1), datetime(2023, 12, 31)),
            "updated": None,
            "role": random.choices(["admin", "user"], weights=[0.2, 0.8])[0]
        }
        
        # Add random updated date for some users
        if random.random() > 0.7:
            user["updated"] = random_date(user["created"], datetime(2024, 3, 21))
            
        users.append(user)
        user_collection.insert_one(user)
        
    print(f"Created {len(users)} users")
    return users

# Create profiles
def create_profiles(users: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """Create user profiles for existing users."""
    profiles = []
    temperature_units = ["C", "F"]
    
    for user in users:
        first_name = fake.first_name()
        last_name = fake.last_name()
        
        # 70% chance to use display name
        display_name = None
        if random.random() > 0.3:
            display_names = [
                f"{first_name}", 
                f"{first_name} {last_name}", 
                f"{first_name[0]}{last_name}", 
                f"{first_name}_{random.randint(1, 100)}"
            ]
            display_name = random.choice(display_names)
            
        # 60% chance to have avatar
        avatar = None
        if random.random() > 0.4:
            avatar = f"https://example.com/avatars/{user['id']}.jpg"
            
        # 80% chance to have phone number
        phone_number = None
        if random.random() > 0.2:
            phone_number = fake.phone_number()
            
        # Select timezone from common options
        timezones = [
            "UTC", "America/New_York", "America/Chicago", "America/Denver", 
            "America/Los_Angeles", "Europe/London", "Europe/Paris", "Asia/Tokyo",
            "Australia/Sydney", "Pacific/Auckland"
        ]
        
        profile = {
            "id": generate_uuid(),
            "user_id": user["id"],
            "first_name": first_name,
            "last_name": last_name,
            "display_name": display_name,
            "avatar": avatar,
            "phone_number": phone_number,
            "timezone": random.choice(timezones),
            "temperature_unit": random.choice(temperature_units),
            "dark_mode": random.random() > 0.5,  # 50% use dark mode
            "favorite_devices": [],  # Will be populated later
            "created": user["created"],
            "updated": user["updated"]
        }
        
        profiles.append(profile)
        profile_collection.insert_one(profile)
        
    print(f"Created {len(profiles)} profiles")
    return profiles

# Create homes (not stored in DB, but used for organization)
def create_homes(users: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """Create homes for users (conceptual, not in database)."""
    homes = []
    
    for user in users:
        # Each user has 1-3 homes
        num_homes = random.choices([1, 2, 3], weights=[0.7, 0.2, 0.1])[0]
        
        for i in range(num_homes):
            home_name = "Main Home"
            if i == 1:
                home_name = random.choice(["Vacation Home", "Beach House", "Cabin", "Lake House"])
            elif i == 2:
                home_name = random.choice(["Rental Property", "Parents' House", "Office"])
                
            home = {
                "id": generate_uuid(),
                "user_id": user["id"],
                "name": home_name,
                "address": fake.address(),
                "created": user["created"]
            }
            homes.append(home)
            
    print(f"Created {len(homes)} conceptual homes")
    return homes

# Create rooms
def create_rooms(homes: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """Create rooms for each home."""
    rooms = []
    
    for home in homes:
        # Determine number of rooms based on home type
        if "Main" in home["name"]:
            num_rooms = random.randint(5, 10)
        elif any(keyword in home["name"] for keyword in ["Vacation", "Beach", "Cabin", "Lake"]):
            num_rooms = random.randint(3, 7)
        else:
            num_rooms = random.randint(2, 5)
            
        # Select random room types without duplicates
        selected_room_types = random.sample(ROOM_TYPES, min(num_rooms, len(ROOM_TYPES)))
        
        # If we need more rooms than unique types, add some numbered bedrooms or generic rooms
        if num_rooms > len(selected_room_types):
            extra_rooms = ["Bedroom " + str(i) for i in range(2, num_rooms - len(selected_room_types) + 2)]
            selected_room_types.extend(extra_rooms)
            
        for room_type in selected_room_types:
            floor = 1
            if room_type in ["Basement", "Garage"]:
                floor = 0
            elif room_type in ["Attic", "Guest Room", "Bedroom 2", "Bedroom 3"]:
                floor = 2
                
            room = {
                "id": generate_uuid(),
                "user_id": home["user_id"],
                "home_id": home["id"],
                "name": room_type,
                "description": f"{room_type} in {home['name']}",
                "type": room_type.lower().replace(" ", "_"),
                "floor": floor,
                "devices": [],  # Will be populated later
                "created": home["created"],
                "updated": None,
                "active": True
            }
            
            # Some rooms have been updated
            if random.random() > 0.7:
                room["updated"] = random_date(home["created"], datetime(2024, 3, 21))
                
            rooms.append(room)
            room_collection.insert_one(room)
            
    print(f"Created {len(rooms)} rooms")
    return rooms

# Create devices
def create_devices(users: List[Dict[str, Any]], rooms: List[Dict[str, Any]], profiles: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """Create devices for each user, assigned to rooms."""
    devices = []
    device_types = list(DEVICE_CAPABILITIES.keys())
    
    # Map users to their rooms
    user_rooms = {}
    for room in rooms:
        if room["user_id"] not in user_rooms:
            user_rooms[room["user_id"]] = []
        user_rooms[room["user_id"]].append(room)
    
    # Create devices for each user
    for user in users:
        if user["id"] not in user_rooms:
            continue
            
        # Get this user's profile
        user_profile = next((p for p in profiles if p["user_id"] == user["id"]), None)
        
        # Find rooms for this user
        user_room_list = user_rooms[user["id"]]
        
        # Determine how many devices this user has (between 5 and 20)
        num_devices = random.randint(5, 20)
        
        # Create devices and assign to rooms
        for _ in range(num_devices):
            # Select random device type
            device_type = random.choice(device_types)
            
            # Select manufacturer for this device type
            manufacturer = random.choice(DEVICE_MANUFACTURERS[device_type])
            
            # Select model for this manufacturer if available, otherwise generic
            if manufacturer in DEVICE_MODELS:
                model = random.choice(DEVICE_MODELS[manufacturer])
            else:
                model = f"{device_type.capitalize()} {random.choice(['Basic', 'Pro', 'Plus', 'Premium'])}"
                
            # Select capabilities for this device type
            capabilities = DEVICE_CAPABILITIES[device_type]
            
            # Select a room
            room = random.choice(user_room_list)
            
            # Create device name based on type and room
            if device_type == "light":
                name_patterns = [
                    f"{room['name']} Light",
                    f"{room['name']} Lamp",
                    f"{room['name']} Ceiling Light",
                    f"{room['name']} Accent Light"
                ]
                name = random.choice(name_patterns)
            elif device_type == "thermostat":
                name = f"{room['name']} Thermostat"
            elif device_type == "lock":
                name_patterns = [
                    f"{room['name']} Door Lock",
                    f"Front Door Lock",
                    f"Back Door Lock",
                    f"Side Door Lock",
                    f"Garage Door Lock"
                ]
                name = random.choice(name_patterns)
            elif device_type == "camera":
                name_patterns = [
                    f"{room['name']} Camera",
                    f"{room['name']} Security Camera",
                    f"Indoor Camera {room['name']}",
                    f"Doorbell Camera"
                ]
                name = random.choice(name_patterns)
            elif device_type == "sensor":
                sensor_types = ["Motion", "Temperature", "Humidity", "Door", "Window", "Water Leak"]
                sensor_type = random.choice(sensor_types)
                name = f"{room['name']} {sensor_type} Sensor"
            elif device_type == "switch":
                name = f"{room['name']} Switch"
            elif device_type == "outlet":
                name_patterns = [
                    f"{room['name']} Outlet",
                    f"{room['name']} Smart Plug",
                    f"{room['name']} Power Outlet"
                ]
                name = random.choice(name_patterns)
            elif device_type == "speaker":
                name_patterns = [
                    f"{room['name']} Speaker",
                    f"{manufacturer} {model} ({room['name']})",
                    f"Smart Speaker {room['name']}"
                ]
                name = random.choice(name_patterns)
            else:
                name = f"{room['name']} {device_type.capitalize()}"
                
            # Random device status with weights
            status_choices = ["online", "offline", "error", "maintenance"]
            status_weights = [0.8, 0.15, 0.03, 0.02]
            status = random.choices(status_choices, weights=status_weights)[0]
            
            # Random settings based on device type
            settings = {}
            if device_type == "light":
                settings = {
                    "brightness": random.randint(0, 100),
                    "color_temp": random.randint(2000, 6500),
                    "on": random.random() > 0.5
                }
                if "color" in capabilities:
                    settings["color"] = {
                        "hue": random.randint(0, 360),
                        "saturation": random.randint(0, 100)
                    }
            elif device_type == "thermostat":
                settings = {
                    "current_temp": round(random.uniform(18, 26), 1),
                    "target_temp": round(random.uniform(20, 24), 1),
                    "mode": random.choice(["heat", "cool", "auto", "off"]),
                    "eco_mode": random.random() > 0.7
                }
            elif device_type == "lock":
                settings = {
                    "locked": random.random() > 0.7,
                    "auto_lock_enabled": random.random() > 0.5,
                    "auto_lock_timeout": random.choice([30, 60, 120, 300])
                }
            
            # Generate IP and MAC for some devices
            ip_address = None
            mac_address = None
            if random.random() > 0.3:  # 70% have IP
                ip_address = fake.ipv4()
                mac_address = ":".join([f"{random.randint(0, 255):02x}" for _ in range(6)])
                
            # Firmware version
            firmware_version = f"{random.randint(1, 5)}.{random.randint(0, 9)}.{random.randint(0, 9)}"
                
            # Create device
            device_id = generate_uuid()
            # Ensure device creation date is valid (not after March 1, 2024)
            device_created_date = random_date(user["created"], datetime(2024, 3, 1))
            device = {
                "id": device_id,
                "name": name,
                "type": device_type,
                "user_id": user["id"],
                "room_id": room["id"],
                "ip_address": ip_address,
                "mac_address": mac_address,
                "manufacturer": manufacturer,
                "model": model,
                "firmware_version": firmware_version,
                "settings": settings,
                "status": status,
                "last_online": datetime.now() - timedelta(minutes=random.randint(0, 1440)) if status != "offline" else None,
                "created": device_created_date,
                "updated": None,
                "capabilities": random.sample(capabilities, min(len(capabilities), random.randint(1, len(capabilities))))
            }
            
            # 40% chance device has been updated
            if random.random() > 0.6:
                device["updated"] = random_date(device["created"], datetime(2024, 3, 21))
                
            devices.append(device)
            device_collection.insert_one(device)
            
            # Add device to room
            room_collection.update_one(
                {"id": room["id"]},
                {"$push": {"devices": device_id}}
            )
            
            # 20% chance this device is a favorite
            if user_profile and random.random() > 0.8:
                profile_collection.update_one(
                    {"user_id": user["id"]},
                    {"$push": {"favorite_devices": device_id}}
                )
                
    print(f"Created {len(devices)} devices")
    return devices

# Create usage data
def create_usage_data(devices: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """Create usage data for devices."""
    usages = []
    
    for device in devices:
        # Skip offline devices
        if device["status"] == "offline":
            continue
            
        # Number of usage records based on device age (1-50 records)
        days_since_creation = (datetime(2024, 3, 21) - device["created"]).days
        num_records = min(50, max(1, int(days_since_creation / 7) + random.randint(1, 5)))
        
        for _ in range(num_records):
            # Generate timestamp within device's lifetime
            timestamp = random_datetime(device["created"], datetime(2024, 3, 21))
            
            # Generate metrics based on device type
            metrics = {}
            duration = None
            energy_consumed = None
            
            if device["type"] == "light":
                duration = random.randint(5, 480)  # 5 mins to 8 hours
                energy_consumed = round(random.uniform(0.01, 0.5), 3)  # kWh
                metrics = {
                    "brightness": random.randint(10, 100),
                    "on_time": duration,
                    "state_changes": random.randint(1, 10)
                }
            elif device["type"] == "thermostat":
                duration = random.randint(30, 1440)  # 30 mins to 24 hours
                energy_consumed = round(random.uniform(0.5, 5), 2)  # kWh
                metrics = {
                    "ambient_temp": round(random.uniform(17, 28), 1),
                    "target_temp": round(random.uniform(19, 25), 1),
                    "heating_time": random.randint(0, duration // 2) if random.random() > 0.5 else 0,
                    "cooling_time": random.randint(0, duration // 2) if random.random() > 0.5 else 0
                }
            elif device["type"] == "lock":
                duration = random.randint(1, 5)  # 1-5 minutes
                metrics = {
                    "locked": random.random() > 0.3,
                    "unlock_count": random.randint(0, 10),
                    "lock_count": random.randint(0, 10),
                    "auto_lock_triggered": random.random() > 0.7
                }
            elif device["type"] == "outlet":
                duration = random.randint(30, 1440)  # 30 mins to 24 hours
                energy_consumed = round(random.uniform(0.1, 10), 2)  # kWh
                metrics = {
                    "power_draw": round(random.uniform(1, 2000), 1),  # watts
                    "voltage": round(random.uniform(110, 120), 1),
                    "current": round(random.uniform(0.1, 15), 2)
                }
            else:
                duration = random.randint(10, 240)  # 10 mins to 4 hours
                if random.random() > 0.7:  # 30% chance for energy data
                    energy_consumed = round(random.uniform(0.05, 2), 2)  # kWh
                metrics = {
                    "usage_minutes": duration,
                    "interactions": random.randint(1, 20)
                }
                
            usage = {
                "id": generate_uuid(),
                "device_id": device["id"],
                "metrics": metrics,
                "timestamp": timestamp,
                "duration": duration,
                "energy_consumed": energy_consumed,
                "status": "active" if random.random() > 0.1 else "idle",
                "created": timestamp,
                "updated": None
            }
            
            usages.append(usage)
            usage_collection.insert_one(usage)
            
    print(f"Created {len(usages)} usage records")
    return usages

# Create automations
def create_automations(users: List[Dict[str, Any]], devices: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """Create automations for users' devices."""
    automations = []
    
    # Map users to their devices
    user_devices = {}
    for device in devices:
        if device["user_id"] not in user_devices:
            user_devices[device["user_id"]] = []
        user_devices[device["user_id"]].append(device)
    
    trigger_types = ["time", "sensor", "manual", "device_state", "location", "weather"]
    action_types = ["device_control", "notification", "scene_activation", "energy_management"]
    
    for user in users:
        if user["id"] not in user_devices:
            continue
            
        # Determine number of automations (2-8)
        num_automations = random.randint(2, 8)
        
        for _ in range(num_automations):
            # Select trigger type
            trigger_type = random.choice(trigger_types)
            
            # Select action type
            action_type = random.choice(action_types)
            
            # Select a device from user's devices
            device = random.choice(user_devices[user["id"]])
            
            # Generate trigger data based on type
            trigger_data = {}
            if trigger_type == "time":
                trigger_data = {
                    "time": f"{random.randint(0, 23):02d}:{random.choice(['00', '15', '30', '45'])}",
                    "days": random.sample(["mon", "tue", "wed", "thu", "fri", "sat", "sun"], 
                                         random.randint(1, 7))
                }
            elif trigger_type == "sensor":
                trigger_data = {
                    "sensor_id": random.choice(user_devices[user["id"]])["id"],
                    "condition": random.choice(["motion_detected", "temperature_above", "temperature_below"]),
                    "threshold": random.randint(15, 30) if "temperature" in trigger_data.get("condition", "") else None
                }
            elif trigger_type == "device_state":
                trigger_data = {
                    "device_id": random.choice(user_devices[user["id"]])["id"],
                    "state": random.choice(["on", "off", "locked", "unlocked"]),
                    "for_duration": random.randint(0, 30) if random.random() > 0.7 else None
                }
            elif trigger_type == "location":
                trigger_data = {
                    "condition": random.choice(["arriving", "leaving"]),
                    "user_ids": [user["id"]]
                }
            elif trigger_type == "weather":
                trigger_data = {
                    "condition": random.choice(["sunny", "rainy", "cloudy", "snowy"]),
                    "temperature_above": random.randint(20, 30) if random.random() > 0.5 else None,
                    "temperature_below": random.randint(0, 15) if random.random() > 0.5 else None
                }
            else:  # manual
                trigger_data = {
                    "button_press": random.choice(["single", "double", "long"]),
                    "device_id": random.choice(user_devices[user["id"]])["id"]
                }
                
            # Generate action data based on type
            action_data = {}
            if action_type == "device_control":
                target_device = random.choice(user_devices[user["id"]])
                if target_device["type"] == "light":
                    action_data = {
                        "device_id": target_device["id"],
                        "action": random.choice(["turn_on", "turn_off", "toggle", "dim"]),
                        "brightness": random.randint(10, 100) if "dim" in action_data.get("action", "") else None
                    }
                elif target_device["type"] == "thermostat":
                    action_data = {
                        "device_id": target_device["id"],
                        "action": random.choice(["set_temperature", "set_mode"]),
                        "temperature": random.randint(18, 26) if "temperature" in action_data.get("action", "") else None,
                        "mode": random.choice(["heat", "cool", "auto", "off"]) if "mode" in action_data.get("action", "") else None
                    }
                else:
                    action_data = {
                        "device_id": target_device["id"],
                        "action": random.choice(["turn_on", "turn_off", "toggle"])
                    }
            elif action_type == "notification":
                action_data = {
                    "title": random.choice([
                        "Home Alert", "Device Status", "Automation Triggered", 
                        "Security Alert", "Energy Notification"
                    ]),
                    "message": random.choice([
                        "Your automation was triggered",
                        f"Device {device['name']} has changed state",
                        "Motion detected in your home",
                        "Temperature threshold reached",
                        "Someone has arrived home"
                    ]),
                    "priority": random.choice(["low", "medium", "high"])
                }
            elif action_type == "scene_activation":
                action_data = {
                    "scene_name": random.choice([
                        "Good Morning", "Good Night", "Movie Time", "Dinner Mode",
                        "Away Mode", "Welcome Home", "Party Mode", "Reading Time"
                    ])
                }
            elif action_type == "energy_management":
                action_data = {
                    "action": random.choice(["eco_mode", "power_saving", "schedule_adjustment"]),
                    "devices": [d["id"] for d in random.sample(
                        user_devices[user["id"]], 
                        random.randint(1, min(3, len(user_devices[user["id"]])))
                    )]
                }
                
            # Create name and description
            if trigger_type == "time":
                name = f"{trigger_data.get('time', '00:00')} {action_data.get('scene_name', '') or action_type.replace('_', ' ').title()}"
            elif trigger_type == "sensor":
                sensor_device = next((d for d in devices if d["id"] == trigger_data.get("sensor_id")), None)
                name = f"When {sensor_device['name'] if sensor_device else 'sensor'} {trigger_data.get('condition', '')}"
            elif trigger_type == "location":
                name = f"When {trigger_data.get('condition', '')} home"
            else:
                name = f"{trigger_type.replace('_', ' ').title()} Automation {random.randint(1, 100)}"
                
            description = f"Automation that triggers when {trigger_type.replace('_', ' ')} and performs {action_type.replace('_', ' ')}"
            
            # Create automation - use safe date range
            end_date = datetime(2024, 2, 1)
            created_date = random_date(device["created"], end_date)
            automation = {
                "id": generate_uuid(),
                "name": name,
                "description": description,
                "user_id": user["id"],
                "device_id": device["id"],
                "enabled": random.random() > 0.2,  # 80% enabled
                "trigger_type": trigger_type,
                "trigger_data": trigger_data,
                "action_type": action_type,
                "action_data": action_data,
                "conditions": None,  # Simplified for now
                "created": created_date,
                "updated": random_date(created_date, datetime(2024, 3, 21)) if random.random() > 0.7 else None,
                "last_triggered": random_date(created_date, datetime(2024, 3, 21)) if random.random() > 0.4 else None,
                "execution_count": random.randint(0, 100)
            }
            
            automations.append(automation)
            automation_collection.insert_one(automation)
            
    print(f"Created {len(automations)} automations")
    return automations

# Create notifications
def create_notifications(users: List[Dict[str, Any]], devices: List[Dict[str, Any]], automations: List[Dict[str, Any]], rooms: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """Create notifications for users."""
    notifications = []
    
    # Notification templates by type
    notification_templates = {
        "alert": [
            {"title": "Motion Detected", "message": "Motion was detected in {room}"},
            {"title": "Door Unlocked", "message": "Your {device} was unlocked"},
            {"title": "Temperature Alert", "message": "Temperature is too {high_low} in {room}"},
            {"title": "Battery Low", "message": "{device} battery is running low"},
            {"title": "Water Leak Detected", "message": "Water leak detected by {device}"}
        ],
        "info": [
            {"title": "Device Offline", "message": "{device} appears to be offline"},
            {"title": "Update Available", "message": "A firmware update is available for {device}"},
            {"title": "Energy Report", "message": "Your weekly energy report is ready"},
            {"title": "New Device Detected", "message": "A new device was detected on your network"},
            {"title": "Automation Created", "message": "Your new automation '{automation}' has been created"}
        ],
        "warning": [
            {"title": "Device Error", "message": "{device} reported an error: {error_code}"},
            {"title": "High Energy Usage", "message": "Your energy usage is {percent}% higher than usual"},
            {"title": "Failed Authentication", "message": "Failed login attempt detected"},
            {"title": "Connection Issues", "message": "{device} is having connectivity problems"},
            {"title": "Hub Offline", "message": "Your smart home hub is offline"}
        ],
        "success": [
            {"title": "Automation Successful", "message": "Automation '{automation}' ran successfully"},
            {"title": "Device Added", "message": "{device} was successfully added to your home"},
            {"title": "Update Completed", "message": "{device} was successfully updated to version {version}"},
            {"title": "Energy Goal Met", "message": "Congratulations! You met your energy saving goal"},
            {"title": "Device Paired", "message": "{device} was successfully paired with your account"}
        ]
    }
    
    for user in users:
        # Determine number of notifications (5-30)
        num_notifications = random.randint(5, 30)
        
        # Get user's devices
        user_devices = [d for d in devices if d["user_id"] == user["id"]]
        if not user_devices:
            continue
            
        # Get user's automations
        user_automations = [a for a in automations if a["user_id"] == user["id"]]
        
        for _ in range(num_notifications):
            # Determine notification type
            notification_type = random.choices(
                ["alert", "info", "warning", "success"],
                weights=[0.2, 0.5, 0.2, 0.1]
            )[0]
            
            # Determine priority
            priority = random.choices(
                ["low", "medium", "high"],
                weights=[0.3, 0.5, 0.2]
            )[0]
            
            # Determine source
            source = random.choices(
                ["device", "system", "automation", "goal", "security"],
                weights=[0.4, 0.3, 0.2, 0.05, 0.05]
            )[0]
            
            # Get template
            template = random.choice(notification_templates[notification_type])
            title = template["title"]
            message = template["message"]
            
            # Fill in placeholders
            source_id = None
            if "{device}" in message or "{device}" in title:
                device = random.choice(user_devices)
                title = title.replace("{device}", device["name"])
                message = message.replace("{device}", device["name"])
                if source == "device":
                    source_id = device["id"]
                    
            if "{room}" in message or "{room}" in title:
                if user_devices:
                    device = random.choice(user_devices)
                    room_id = device["room_id"]
                    room = next((r for r in rooms if r["id"] == room_id), None)
                    if room:
                        title = title.replace("{room}", room["name"])
                        message = message.replace("{room}", room["name"])
                        
            if "{automation}" in message or "{automation}" in title:
                if user_automations:
                    automation = random.choice(user_automations)
                    title = title.replace("{automation}", automation["name"])
                    message = message.replace("{automation}", automation["name"])
                    if source == "automation":
                        source_id = automation["id"]
                        
            if "{high_low}" in message:
                message = message.replace("{high_low}", random.choice(["high", "low"]))
                
            if "{percent}" in message:
                message = message.replace("{percent}", str(random.randint(15, 50)))
                
            if "{error_code}" in message:
                message = message.replace("{error_code}", f"E{random.randint(100, 999)}")
                
            if "{version}" in message:
                message = message.replace("{version}", f"{random.randint(1,5)}.{random.randint(0,9)}.{random.randint(0,9)}")
                
            # Determine timestamp
            timestamp = random_datetime(datetime(2024, 1, 1), datetime(2024, 3, 21))
            
            # Determine read status (older = more likely to be read)
            days_old = (datetime(2024, 3, 21) - timestamp).days
            read_probability = min(0.9, days_old / 30)  # Older than 30 days = 90% read
            read = random.random() < read_probability
            
            # Create read timestamp if read
            read_timestamp = None
            if read:
                read_timestamp = timestamp + timedelta(minutes=random.randint(1, 1440))  # 1 min to 1 day later
                
            notification = {
                "id": generate_uuid(),
                "user_id": user["id"],
                "title": title,
                "message": message,
                "type": notification_type,
                "priority": priority,
                "source": source,
                "source_id": source_id,
                "read": read,
                "timestamp": timestamp,
                "read_timestamp": read_timestamp
            }
            
            notifications.append(notification)
            notification_collection.insert_one(notification)
            
    print(f"Created {len(notifications)} notifications")
    return notifications

# Create access management entries
def create_access_management(users: List[Dict[str, Any]], devices: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """Create access management entries for sharing resources."""
    access_entries = []
    
    # For each user who has devices
    for user in users:
        user_devices = [d for d in devices if d["user_id"] == user["id"]]
        if not user_devices:
            continue
            
        # Determine if this user shares devices (40% chance)
        if random.random() > 0.6:
            # Find possible recipients (other users)
            other_users = [u for u in users if u["id"] != user["id"]]
            if not other_users:
                continue
                
            # Determine how many devices to share (1-3)
            num_shares = random.randint(1, min(3, len(user_devices)))
            
            # Select devices to share
            devices_to_share = random.sample(user_devices, num_shares)
            
            # For each device, create sharing
            for device in devices_to_share:
                # Choose 1-3 users to share with
                share_recipients = random.sample(other_users, random.randint(1, min(3, len(other_users))))
                
                # Determine access level
                access_level = random.choice(["read", "control", "manage"])
                
                # Determine if there's an expiration (30% chance)
                expires_at = None
                if random.random() > 0.7:
                    # Expire 1-30 days from now
                    expires_at = datetime.now() + timedelta(days=random.randint(1, 30))
                    
                # Create note (50% chance)
                note = None
                if random.random() > 0.5:
                    note_templates = [
                        f"Sharing {device['name']} with family",
                        f"Temporary access for house sitting",
                        f"Guest access to {device['name']}",
                        f"Please don't change the settings",
                        f"Access for the weekend"
                    ]
                    note = random.choice(note_templates)
                    
                # Create access entry for each recipient
                for recipient in share_recipients:
                    access_entry = {
                        "id": generate_uuid(),
                        "owner_id": user["id"],
                        "resource_id": device["id"],
                        "resource_type": "device",  # Simplified - could also be room, home, etc.
                        "user_id": recipient["id"],
                        "access_level": access_level,
                        "created": random_date(device["created"], datetime(2024, 2, 15)),
                        "updated": None,
                        "expires_at": expires_at,
                        "active": True,
                        "note": note
                    }
                    
                    # 30% chance of update
                    if random.random() > 0.7:
                        access_entry["updated"] = random_date(access_entry["created"], datetime(2024, 3, 21))
                        
                    access_entries.append(access_entry)
                    access_management_collection.insert_one(access_entry)
                    
    print(f"Created {len(access_entries)} access management entries")
    return access_entries

# Create energy goals
def create_energy_goals(users: List[Dict[str, Any]], devices: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """Create energy saving goals for users."""
    goals = []
    
    # Goal templates
    goal_templates = [
        {
            "title": "Reduce Monthly Energy Usage",
            "description": "Goal to reduce total energy consumption by {target_value}% compared to last month.",
            "type": "energy_saving"
        },
        {
            "title": "Limit Peak Hour Consumption",
            "description": "Reduce energy usage during peak hours (6-9pm) to less than {target_value} kWh per day.",
            "type": "consumption_limit"
        },
        {
            "title": "Lower Standby Power Usage",
            "description": "Reduce standby power consumption by {target_value}% by optimizing device settings.",
            "type": "usage_reduction"
        },
        {
            "title": "Avoid Peak Demand Charges",
            "description": "Keep peak demand below {target_value} kW to avoid extra charges on your utility bill.",
            "type": "peak_avoidance"
        },
        {
            "title": "Increase Renewable Energy Usage",
            "description": "Shift {target_value}% of energy consumption to hours with higher renewable energy availability.",
            "type": "renewable_usage"
        }
    ]
    
    for user in users:
        # 60% chance user has goals
        if random.random() > 0.4:
            # Get user's devices
            user_devices = [d for d in devices if d["user_id"] == user["id"]]
            if not user_devices:
                continue
                
            # Determine number of goals (1-3)
            num_goals = random.randint(1, 3)
            
            for _ in range(num_goals):
                # Choose template
                template = random.choice(goal_templates)
                
                # Determine timeframe
                timeframe = random.choice(["daily", "weekly", "monthly", "yearly"])
                
                # Set target value based on goal type
                if template["type"] == "energy_saving" or template["type"] == "usage_reduction":
                    target_value = random.randint(5, 25)  # Percent reduction
                elif template["type"] == "consumption_limit":
                    target_value = random.randint(5, 20)  # kWh limit
                elif template["type"] == "peak_avoidance":
                    target_value = random.randint(3, 8)  # kW limit
                else:  # renewable_usage
                    target_value = random.randint(20, 50)  # Percent of renewable
                    
                # Fill in description
                description = template["description"].replace("{target_value}", str(target_value))
                
                # Determine start date
                start_date = random_date(datetime(2024, 1, 1), datetime(2024, 3, 1))
                
                # Determine end date based on timeframe
                end_date = None
                if timeframe == "daily":
                    end_date = start_date + timedelta(days=1)
                elif timeframe == "weekly":
                    end_date = start_date + timedelta(weeks=1)
                elif timeframe == "monthly":
                    end_date = start_date + timedelta(days=30)
                elif timeframe == "yearly":
                    end_date = start_date + timedelta(days=365)
                else:  # custom
                    end_date = start_date + timedelta(days=random.randint(7, 90))
                    
                # Determine related devices (if any)
                related_devices = []
                if random.random() > 0.3:  # 70% chance of related devices
                    num_related = random.randint(1, min(5, len(user_devices)))
                    related_devices = [d["id"] for d in random.sample(user_devices, num_related)]
                    
                # Determine current progress
                current_value = 0
                progress_percentage = 0
                
                # If goal is in the past or ongoing, set some progress
                if end_date < datetime.now() or random.random() > 0.5:
                    if template["type"] == "energy_saving" or template["type"] == "usage_reduction":
                        current_value = random.randint(1, target_value)
                    elif template["type"] == "consumption_limit":
                        current_value = random.randint(target_value - 5, target_value + 5)
                    elif template["type"] == "peak_avoidance":
                        current_value = random.randint(target_value - 2, target_value + 2)
                    else:  # renewable_usage
                        current_value = random.randint(1, target_value)
                        
                    progress_percentage = min(100, int((current_value / target_value) * 100))
                    
                # Determine status
                if end_date < datetime.now():
                    if progress_percentage >= 100:
                        status = "completed"
                    else:
                        status = "failed"
                else:
                    status = random.choice(["active", "paused"]) if random.random() > 0.2 else "active"
                    
                goal = {
                    "id": generate_uuid(),
                    "user_id": user["id"],
                    "title": template["title"],
                    "description": description,
                    "type": template["type"],
                    "target_value": float(target_value),
                    "current_value": float(current_value),
                    "progress_percentage": float(progress_percentage),
                    "timeframe": timeframe,
                    "start_date": start_date,
                    "end_date": end_date,
                    "status": status,
                    "related_devices": related_devices,
                    "created": start_date - timedelta(days=random.randint(1, 7)),
                    "updated": random_date(start_date, datetime(2024, 3, 21)) if random.random() > 0.5 else None
                }
                
                goals.append(goal)
                goal_collection.insert_one(goal)
                
    print(f"Created {len(goals)} energy goals")
    return goals

# Create analytics data
def create_analytics(users: List[Dict[str, Any]], devices: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """Create analytics data for devices."""
    analytics_entries = []
    data_types = ["energy", "usage", "temperature", "humidity", "motion", "light"]
    
    for device in devices:
        # Skip offline devices
        if device["status"] == "offline":
            continue
            
        # Determine appropriate data types for this device
        applicable_types = []
        if device["type"] == "light":
            applicable_types = ["energy", "usage", "light"]
        elif device["type"] == "thermostat":
            applicable_types = ["energy", "temperature", "humidity"]
        elif device["type"] == "lock":
            applicable_types = ["usage"]
        elif device["type"] == "camera":
            applicable_types = ["usage", "motion"]
        elif device["type"] == "sensor":
            # Determine sensor type from name
            sensor_type = "motion"  # default
            if "temperature" in device["name"].lower():
                applicable_types = ["temperature"]
            elif "humidity" in device["name"].lower():
                applicable_types = ["humidity"]
            elif "motion" in device["name"].lower():
                applicable_types = ["motion"]
            elif "light" in device["name"].lower():
                applicable_types = ["light"]
            else:
                applicable_types = [random.choice(data_types)]
        elif device["type"] == "outlet":
            applicable_types = ["energy", "usage"]
        else:
            applicable_types = ["energy", "usage"]
            
        # Determine number of analytics entries (1-20)
        num_entries = random.randint(1, 20)
        
        for _ in range(num_entries):
            # Choose data type
            data_type = random.choice(applicable_types)
            
            # Generate metrics based on data type
            metrics = {}
            if data_type == "energy":
                metrics = {
                    "consumption": round(random.uniform(0.1, 10), 3),  # kWh
                    "cost": round(random.uniform(0.01, 1.5), 2),  # $
                    "duration": random.randint(10, 1440)  # minutes
                }
            elif data_type == "usage":
                metrics = {
                    "duration": random.randint(10, 480),  # minutes
                    "interactions": random.randint(1, 50),
                    "active_time": random.randint(5, 200)  # minutes
                }
            elif data_type == "temperature":
                metrics = {
                    "value": round(random.uniform(18, 26), 1),  # Celsius
                    "setpoint": round(random.uniform(20, 24), 1),  # Celsius
                    "outside_temp": round(random.uniform(10, 35), 1)  # Celsius
                }
            elif data_type == "humidity":
                metrics = {
                    "value": random.randint(30, 70),  # Percent
                    "comfort_zone": random.choice(["low", "optimal", "high"])
                }
            elif data_type == "motion":
                metrics = {
                    "detected": random.random() > 0.3,
                    "duration": random.randint(0, 120) if metrics.get("detected", False) else 0,
                    "peak_time": f"{random.randint(0, 23):02d}:{random.choice(['00', '15', '30', '45'])}"
                }
            elif data_type == "light":
                metrics = {
                    "level": random.randint(0, 100),  # Percent
                    "color_temp": random.randint(2000, 6500),  # Kelvin
                    "is_natural": random.random() > 0.5
                }
                
            # Generate tags
            tags = []
            if random.random() > 0.4:  # 60% have tags
                possible_tags = ["daily", "weekly", "monthly", "peak", "off-peak", "weekend", "weekday"]
                num_tags = random.randint(1, 3)
                tags = random.sample(possible_tags, num_tags)
                
            # Create analytics entry
            timestamp = random_datetime(device["created"], datetime(2024, 3, 21))
            analytics_entry = {
                "id": generate_uuid(),
                "user_id": device["user_id"],
                "device_id": device["id"],
                "data_type": data_type,
                "metrics": metrics,
                "tags": tags,
                "timestamp": timestamp,
                "updated": None
            }
            
            # 20% chance of update
            if random.random() > 0.8:
                analytics_entry["updated"] = timestamp + timedelta(minutes=random.randint(5, 60))
                
            analytics_entries.append(analytics_entry)
            analytics_collection.insert_one(analytics_entry)
            
    print(f"Created {len(analytics_entries)} analytics entries")
    return analytics_entries

# Create suggestions
def create_suggestions(users: List[Dict[str, Any]], devices: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """Create suggestions for users to improve their smart home."""
    suggestions = []
    
    # Suggestion templates by type
    suggestion_templates = {
        "energy_saving": [
            {"title": "Optimize Thermostat Schedule", 
             "description": "Based on your usage patterns, adjusting your thermostat schedule could save up to 15% on heating and cooling costs. We suggest lowering temperatures at night and when you're away from home."},
            {"title": "Replace High-Energy Light Bulbs", 
             "description": "Some of your lights are using older technology. Replacing them with LED bulbs could reduce lighting energy consumption by up to 80%."},
            {"title": "Smart Power Strip for Entertainment Center", 
             "description": "Your entertainment devices are drawing standby power. Using a smart power strip could eliminate this vampire power and save up to $100 annually."},
            {"title": "Install Motion Sensors for Lights", 
             "description": "We've noticed lights staying on in unoccupied rooms. Adding motion sensors could reduce wasted electricity by automatically turning off lights when rooms are empty."},
            {"title": "Schedule Device Power Down", 
             "description": "Creating a nighttime automation to power down non-essential devices could reduce your overnight energy consumption by up to 12%."}
        ],
        "security": [
            {"title": "Add Entry Sensors to Windows", 
             "description": "Your home security could be improved by adding entry sensors to ground-floor windows. This would alert you immediately if a window is opened unexpectedly."},
            {"title": "Improve Door Lock Security", 
             "description": "Your front door lock doesn't have auto-lock enabled. We recommend enabling this feature to ensure your door locks automatically after being unlocked."},
            {"title": "Set Up Camera Motion Zones", 
             "description": "Your security cameras could be more effective by setting up specific motion zones to reduce false alerts and focus on important areas."},
            {"title": "Create Lighting Schedules When Away", 
             "description": "Setting up randomized lighting schedules when you're away can deter potential intruders by simulating occupancy."},
            {"title": "Enable Two-Factor Authentication", 
             "description": "For improved account security, enable two-factor authentication for your smart home system access."}
        ],
        "comfort": [
            {"title": "Optimize Temperature for Better Sleep", 
             "description": "Research shows sleeping in slightly cooler temperatures improves sleep quality. We suggest setting your bedroom to 65-68°F (18-20°C) overnight."},
            {"title": "Create Morning Routine Automation", 
             "description": "Start your day right with a morning routine that gradually turns on lights, adjusts the thermostat, and plays your favorite music at wake-up time."},
            {"title": "Add Humidity Control to Bedrooms", 
             "description": "The humidity levels in your bedrooms fluctuate outside the ideal 40-60% range. A smart humidifier could improve air quality and comfort."},
            {"title": "Set Up Optimal Lighting Scenes", 
             "description": "Creating preset lighting scenes for different activities (reading, movie watching, dinner) can enhance mood and comfort in your living spaces."},
            {"title": "Automate Blinds for Natural Light", 
             "description": "Adding smart blinds that automatically adjust based on time of day and sunlight can optimize natural light while maintaining privacy."}
        ],
        "automation": [
            {"title": "Create Arriving/Leaving Home Routines", 
             "description": "Set up geofencing to automatically adjust your home when you arrive or leave - turning on/off lights, adjusting temperature, and securing doors."},
            {"title": "Link Weather to Home Behavior", 
             "description": "Connect your system to weather forecasts to automatically close blinds during hot days or adjust heating before cold fronts arrive."},
            {"title": "Set Up Night Mode Routine", 
             "description": "Create a bedtime routine that secures your home, dims lights, and creates the optimal sleeping environment with a single command."},
            {"title": "Voice Command Shortcuts", 
             "description": "We've identified common device combinations you use. Setting up custom voice commands could make controlling these groups more convenient."},
            {"title": "Automate Based on Occupancy", 
             "description": "Using your motion sensors to automatically control lights and climate based on which rooms are occupied could improve convenience and efficiency."}
        ]
    }
    
    for user in users:
        # 70% chance user has suggestions
        if random.random() > 0.3:
            # Get user's devices
            user_devices = [d for d in devices if d["user_id"] == user["id"]]
            if not user_devices:
                continue
                
            # Determine number of suggestions (2-10)
            num_suggestions = random.randint(2, 10)
            
            for _ in range(num_suggestions):
                # Choose suggestion type
                suggestion_type = random.choice(list(suggestion_templates.keys()))
                
                # Choose template
                template = random.choice(suggestion_templates[suggestion_type])
                
                # Determine priority
                priority = random.randint(1, 5)
                
                # Determine related devices
                related_device_ids = None
                if random.random() > 0.3:  # 70% have related devices
                    num_related = random.randint(1, min(3, len(user_devices)))
                    related_device_ids = [d["id"] for d in random.sample(user_devices, num_related)]
                    
                # Determine status
                status_weights = [0.4, 0.3, 0.2, 0.1]  # pending, accepted, rejected, implemented
                status = random.choices(["pending", "accepted", "rejected", "implemented"], weights=status_weights)[0]
                
                # Create timestamps
                created = random_date(datetime(2024, 1, 1), datetime(2024, 3, 15))
                updated = None
                implemented_date = None
                user_feedback = None
                
                # If not pending, add update info
                if status != "pending":
                    updated = created + timedelta(days=random.randint(1, 14))
                    
                    if status == "implemented":
                        implemented_date = updated + timedelta(days=random.randint(1, 7))
                        
                    if random.random() > 0.5:  # 50% chance of feedback
                        if status == "accepted" or status == "implemented":
                            feedback_options = [
                                "Great suggestion, I'll try this.",
                                "This is exactly what I needed.",
                                "Thanks for the recommendation!",
                                "I've been looking for something like this."
                            ]
                        else:  # rejected
                            feedback_options = [
                                "Not interested in this right now.",
                                "I've tried this before and it didn't work for me.",
                                "Maybe later, but not a priority.",
                                "I prefer my current setup."
                            ]
                        user_feedback = random.choice(feedback_options)
                
                suggestion = {
                    "id": generate_uuid(),
                    "user_id": user["id"],
                    "title": template["title"],
                    "description": template["description"],
                    "type": suggestion_type,
                    "priority": priority,
                    "status": status,
                    "related_device_ids": related_device_ids,
                    "created": created,
                    "updated": updated,
                    "implemented_date": implemented_date,
                    "user_feedback": user_feedback
                }
                
                suggestions.append(suggestion)
                suggestion_collection.insert_one(suggestion)
                
    print(f"Created {len(suggestions)} suggestions")
    return suggestions

# Main function to run all seeding
def seed_database():
    print("Starting database seeding...")
    
    # Clear existing data
    clear_collections()
    
    # Create data in proper order (respect dependencies)
    users = create_users(25)  # 25 users
    profiles = create_profiles(users)
    homes = create_homes(users)  # Conceptual, not stored
    rooms = create_rooms(homes)
    devices = create_devices(users, rooms, profiles)
    usage_data = create_usage_data(devices)
    automations = create_automations(users, devices)
    notifications = create_notifications(users, devices, automations, rooms)
    access_management = create_access_management(users, devices)
    goals = create_energy_goals(users, devices)
    analytics = create_analytics(users, devices)
    suggestions = create_suggestions(users, devices)
    
    print("Database seeding completed successfully!")
    print(f"""
    Summary:
    - {len(users)} users
    - {len(profiles)} profiles
    - {len(rooms)} rooms
    - {len(devices)} devices
    - {len(usage_data)} usage records
    - {len(automations)} automations
    - {len(notifications)} notifications
    - {len(access_management)} access management entries
    - {len(goals)} energy goals
    - {len(analytics)} analytics entries
    - {len(suggestions)} suggestions
    """)

if __name__ == "__main__":
    seed_database()
