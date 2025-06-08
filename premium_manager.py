# strangemind_ai/premium_manager.py

from pymongo import MongoClient
from datetime import datetime, timedelta
import os

# Load MongoDB URI from environment variables
MONGO_URI = os.getenv("MONGO_URI", "mongodb://localhost:27017/")
DB_NAME = "strangemindDB"
COLLECTION_NAME = "premium_users"

# Connect to MongoDB
client = MongoClient(MONGO_URI)
db = client[DB_NAME]
premium_collection = db[COLLECTION_NAME]


def add_premium_user(phone_number, duration_days=30):
    """
    Adds or renews a premium user subscription.
    phone_number: string e.g. "+2348012345678"
    duration_days: int, length of subscription in days (default 30)
    """
    now = datetime.utcnow()
    user = premium_collection.find_one({"phone": phone_number})

    if user:
        # Renew from current expiry or now, whichever is later
        current_expiry = user.get("expiry", now)
        new_expiry = max(current_expiry, now) + timedelta(days=duration_days)
        premium_collection.update_one(
            {"phone": phone_number},
            {"$set": {"expiry": new_expiry}}
        )
    else:
        new_expiry = now + timedelta(days=duration_days)
        premium_collection.insert_one({
            "phone": phone_number,
            "expiry": new_expiry
        })

    return new_expiry


def revoke_premium(phone_number):
    """
    Revokes premium status immediately by deleting the record.
    """
    result = premium_collection.delete_one({"phone": phone_number})
    return result.deleted_count > 0


def is_user_premium(phone_number):
    """
    Checks if user currently has a valid premium subscription.
    Returns True if active, False otherwise.
    """
    now = datetime.utcnow()
    user = premium_collection.find_one({"phone": phone_number})

    if user and user.get("expiry") and user["expiry"] > now:
        return True
    return False


def get_premium_expiry(phone_number):
    """
    Returns expiry datetime of user's premium subscription or None.
    """
    user = premium_collection.find_one({"phone": phone_number})
    return user.get("expiry") if user else None


if __name__ == "__main__":
    # Quick test (run python premium_manager.py)
    test_phone = "+2348012345678"
    print(f"Adding premium for {test_phone} for 30 days...")
    expiry = add_premium_user(test_phone)
    print(f"Expires on: {expiry}")

    print(f"Checking premium status for {test_phone}...")
    print(is_user_premium(test_phone))

    print(f"Revoking premium for {test_phone}...")
    revoke_premium(test_phone)

    print(f"Checking premium status for {test_phone} after revoke...")
    print(is_user_premium(test_phone))
