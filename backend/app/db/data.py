"""
Handles MongoDB database connections & operations.
"""
import os       # Connection to external database
from pymongo import MongoClient

MONGO_URI = os.getenv("MONGO_URI", "mongodb://localhost:27017/")

# Initializing client
try:
    c = MongoClient(MONGO_URI)
    d = c.sync

    u_c = d["user"]                 # User collection
    p_c = d["profile"]              # Profile collection
    d_c = d["device"]               # Device collection
    r_c = d["room"]                 # Room collection
    us_c = d["usage"]               # Usage collection
    a_c = d["automation"]           # Automation collection
    n_c = d["notification"]         # Notification collection
    am_c = d["access management"]   # Access Management collection
    g_c = d["goal"]                 # Energy Goal collection
    an_c = d["analytics"]           # Analytics collection
    s_c = d["suggestion"]           # Suggestion collection

    print(f"Connected to MongoDB database: {MONGO_URI}")
except Exception as e:
    raise ConnectionError(f"Failed to connect to MongoDB: {e}") from e


def init_db():
    """
    Initialize MongoDB database & creates indexes.
    """
    # User collection
    u_c.create_index("id", unique=True)     # Unique identification
    u_c.create_index("email", unique=True)  # Unique email address
    u_c.create_index("username")            # General username

    # Profile collection
    p_c.create_index("id", unique=True)         # Unique identification
    p_c.create_index("user_id", unique=True)    # Unique user identification

    # Device collection
    d_c.create_index("id", unique=True)             # Device identification
    d_c.create_index("user_id")                     # User identification
    d_c.create_index([("type", 1), ("user_id", 1)]) # Filter type through user identification

    # Room collection
    r_c.create_index("id", unique=True)     # Unique identification
    r_c.create_index("user_id")             # User identification
    r_c.create_index("home_id")             # Home identification

    # Usage collection
    us_c.create_index("id", unique=True)                     # Unique identification
    us_c.create_index("device_id")                           # Device identification
    us_c.create_index("timestamp")                           # Usage log
    us_c.create_index([("device_id", 1), ("timestamp", -1)])  # Filter log by device identification

    # Automation collection
    a_c.create_index("id", unique=True)     # Unique identification
    a_c.create_index("user_id")             # User identification
    a_c.create_index("device_id")           # User identification

    # Notification collection
    n_c.create_index("id", unique=True)                                 # Unique identification
    n_c.create_index("user_id")                                         # User identification
    n_c.create_index([("user_id", 1), ("read", 1), ("timestamp", -1)])  # Filter notification read by device & time

    # Access Management collection
    am_c.create_index("id", unique=True)                        # Unique identification
    am_c.create_index("owner_id")                               # Owner identification
    am_c.create_index("resource_id")                            # Resource identification
    am_c.create_index([("owner_id", 1), ("resource_id", 1)])    # Filters resource by its owner

    # Goal collection
    g_c.create_index("id", unique=True)                 # Unique identification
    g_c.create_index("user_id")                         # User identification
    g_c.create_index("type")                            # Type of goal
    g_c.create_index([("user_id", 1), ("type", 1)])     # Filters types of goals by user identification

    # Analytics collection
    an_c.create_index("id", unique=True)                    # Unique identification
    an_c.create_index("user_id")                            # User identification
    an_c.create_index("device_id")                          # Device identification
    an_c.create_index([("user_id", 1), ("timestamp", -1)])  # Filters user identification by timestamp

    # Suggestion collection
    s_c.create_index("id", unique=True)                                     # Unique identification
    s_c.create_index("user_id")                                             # User identification
    s_c.create_index([("user_id", 1), ("status", 1), ("timestamp", -1)])    # Filters user identification with status by timestamp

    print("Database initialized with indexes.")
