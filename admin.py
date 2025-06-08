# Imports
import os
from scraper import aggregate_search, youtube_search
from utils import send_whatsapp_message  # Your existing WhatsApp send function

from pymongo import MongoClient
from config import MONGO_URI, ADMIN_PHONE

# MongoDB setup
client = MongoClient(MONGO_URI)
db = client.strangemindDB
users_collection = db.contacts
groups_collection = db.groups
premium_collection = db.premium_users

ADMIN_PHONE = ADMIN_PHONE.strip()

# Premium user management functions
def is_admin(phone: str):
    """Checks if the sender is the main admin."""
    return phone == ADMIN_PHONE

def grant_premium(phone: str, is_group=False):
    """Grants premium access to a user or group."""
    collection = groups_collection if is_group else users_collection
    result = collection.update_one(
        {"phone": phone},
        {"$set": {"is_premium": True}},
        upsert=True
    )
    premium_collection.update_one(
        {"phone": phone},
        {"$set": {"premium": True}},
        upsert=True
    )
    return result.modified_count > 0

def revoke_premium(phone: str, is_group=False):
    """Revokes premium access from a user or group."""
    collection = groups_collection if is_group else users_collection
    result = collection.update_one(
        {"phone": phone},
        {"$set": {"is_premium": False}}
    )
    premium_collection.update_one(
        {"phone": phone},
        {"$set": {"premium": False}},
        upsert=True
    )
    return result.modified_count > 0

def check_premium(phone: str, is_group=False):
    """Checks if a user or group has premium status."""
    collection = groups_collection if is_group else users_collection
    record = collection.find_one({"phone": phone})
    fallback = premium_collection.find_one({"phone": phone})

    if record and record.get("is_premium", False):
        return True
    elif fallback and fallback.get("premium", False):
        return True
    return False

# Your Movie + YouTube integration handler
TMDB_API_KEY = os.getenv("TMDB_API_KEY")
YOUTUBE_API_KEY = os.getenv("YOUTUBE_API_KEY")

def handle_movie_command(user_phone, query):
    # Check premium status before processing heavy requests (optional but recommended)
    if not check_premium(user_phone):
        send_whatsapp_message(user_phone, "⚠️ This feature is for premium users only. Please upgrade to access movie searches and trailers.")
        return

    # Aggregate movie + torrent + TMDB results
    movie_results = aggregate_search(query, tmdb_api_key=TMDB_API_KEY)
    # Get YouTube trailers
    trailer_results = youtube_search(query, max_results=3, youtube_api_key=YOUTUBE_API_KEY)

    # Build response message
    message = f"🎬 Results for \"{query}\":\n\n"
    for idx, movie in enumerate(movie_results[:5], 1):
        message += f"{idx}️⃣ {movie['title']}\nLink: {movie['link']}\nSource: {movie['source']}\n\n"

    if trailer_results:
        message += "🎥 YouTube Trailers:\n"
        for trailer in trailer_results:
            message += f"- {trailer['title']}: {trailer['url']}\n"

    send_whatsapp_message(user_phone, message)

# Example usage to test premium management (optional)
if __name__ == "__main__":
    test_user = "+2348012345678"

    print("✅ Granting premium to test user...")
    print(grant_premium(test_user))  # True if success

    print("🔍 Checking premium status...")
    print(check_premium(test_user))  # True

    print("❌ Revoking premium...")
    print(revoke_premium(test_user))  # True

    print("🔍 Re-checking premium...")
    print(check_premium(test_user))  # False
