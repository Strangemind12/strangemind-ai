import os
import requests
from datetime import datetime, timedelta
from collections import defaultdict
from pymongo import MongoClient
from config import MONGO_URI, ADMIN_PHONE

# --- MongoDB Setup ---
client = MongoClient(MONGO_URI)
db = client.strangemindDB

# Collections
vault_collection = db.vault

# --- Spam Guard Setup ---

# Memory map for rate limiting and behavior (replace with Redis/DB in prod)
message_history = defaultdict(list)

# Combine all spam keywords here
blacklist_words = [
    "scam", "fraud", "nude", "curseword1", "curseword2",
    "buy now", "free money", "click here", "subscribe", "cheap", "offer"
]

rate_limit_count = 5
rate_limit_seconds = 10

def is_spammy(message: str) -> bool:
    msg = message.lower()
    return any(word in msg for word in blacklist_words)

def is_rate_limited(phone: str) -> bool:
    now = datetime.utcnow()
    recent = [t for t in message_history[phone] if now - t < timedelta(seconds=rate_limit_seconds)]
    message_history[phone] = recent + [now]
    return len(recent) >= rate_limit_count

def detect_abuse(phone: str, message: str) -> str | None:
    if is_spammy(message):
        return "🚫 Inappropriate or spammy language detected. Please follow the rules."
    if is_rate_limited(phone):
        return "🕒 You're messaging too fast. Please wait a moment."
    return None

# --- Vault Management ---

def shorten_link(url: str) -> str:
    # You can replace this with your monetized shortener service later
    return url  # your existing placeholder logic

def get_vault_balance(phone: str) -> float:
    vault = vault_collection.find_one({"user": phone})
    if vault:
        return vault.get("balance", 0)
    return 0

def withdraw_from_vault(phone: str, amount: float) -> bool:
    vault = vault_collection.find_one({"user": phone})
    if vault and vault.get("balance", 0) >= amount:
        vault_collection.update_one({"user": phone}, {"$inc": {"balance": -amount}})
        return True
    return False

def is_admin(phone: str) -> bool:
    # Use config ADMIN_PHONE if set; else fallback to your dummy "admin"
    if ADMIN_PHONE:
        return phone == ADMIN_PHONE
    return phone == "admin"

# --- YouTube Search ---

YOUTUBE_API_KEY = os.getenv("YOUTUBE_API_KEY")

def youtube_search(query: str, max_results=3):
    if not YOUTUBE_API_KEY:
        # Fallback dummy search if no API key provided
        return [{"url": f"https://youtube.com/watch?v=dQw4w9WgXcQ&search={query}"}]

    url = "https://www.googleapis.com/youtube/v3/search"
    params = {
        "part": "snippet",
        "q": query + " trailer",
        "key": YOUTUBE_API_KEY,
        "maxResults": max_results,
        "type": "video"
    }
    response = requests.get(url, params=params)
    if response.status_code != 200:
        return []

    items = response.json().get("items", [])
    results = []
    for item in items:
        video_id = item["id"]["videoId"]
        snippet = item["snippet"]
        results.append({
            "title": snippet["title"],
            "url": f"https://youtu.be/{video_id}",
            "channel": snippet.get("channelTitle", "Unknown"),
            "thumbnail": snippet["thumbnails"]["high"]["url"]
        })
    return results
