import os
import requests
from datetime import datetime, timedelta
from collections import defaultdict
from pymongo import MongoClient
from flask import Flask, request, jsonify

# --- MongoDB Setup ---
MONGO_URI = os.getenv("MONGO_URI", "mongodb://localhost:27017/")
client = MongoClient(MONGO_URI)
db = client.strangemindDB  # unified DB name

# Collections
premium_users_col = db.premium_users
users_col = db.contacts
vault_collection = db.vault
history_collection = db.history

# --- Flask Setup ---
app = Flask(__name__)

# --- Rate Limiting and Spam Setup ---
message_history = defaultdict(list)
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

# --- Short Link Shortener ---
def shorten_link(url: str) -> str:
    api_key = os.getenv("SHRINKEARN_API_KEY")  # Set your ShrinkEarn API key in environment
    if not api_key:
        return url  # fallback no-shortening

    api_url = f"https://shrinkearn.com/api?api={api_key}&url={url}"
    try:
        res = requests.get(api_url)
        return res.json().get("shortenedUrl", url)
    except Exception as e:
        print("Shortener Error:", e)
        return url

# --- Auto-save Contact ---
def save_contact(phone: str, name: str):
    existing = users_col.find_one({"phone": phone})
    if not existing:
        users_col.insert_one({
            "phone": phone,
            "name": name or "Unknown",
            "joined": datetime.utcnow(),
            "is_premium": False,
            "referral_code": None,
            "referred_by": None
        })

# --- Premium User Logic ---
def is_premium_user(phone: str) -> bool:
    user = users_col.find_one({"phone": phone})
    if not user:
        return False
    expiry = user.get("premium_expiry")
    if expiry and expiry > datetime.utcnow():
        return True
    # Auto-revoke if expired
    if user.get("is_premium"):
        users_col.update_one({"phone": phone}, {"$set": {"is_premium": False, "premium_expiry": None}})
    return False

def grant_premium(phone: str, days: int = 30):
    expiry_date = datetime.utcnow() + timedelta(days=days)
    users_col.update_one(
        {"phone": phone},
        {
            "$set": {
                "is_premium": True,
                "premium_expiry": expiry_date,
                "subscribed_at": datetime.utcnow()
            }
        },
        upsert=True
    )
    return expiry_date

# --- Save User Activity ---
def save_activity(phone: str, action: str, data: dict):
    history_collection.insert_one({
        "phone": phone,
        "action": action,
        "data": data,
        "timestamp": datetime.utcnow()
    })

# --- Dummy Movie Search & YouTube Trailer ---
def aggregate_search(query: str, api_key: str):
    # Placeholder for actual TMDB API search logic
    # For demo, return dummy list with 'link' field
    return [
        {"title": f"Movie 1 matching {query}", "link": "https://example.com/movie1"},
        {"title": f"Movie 2 matching {query}", "link": "https://example.com/movie2"},
        {"title": f"Movie 3 matching {query}", "link": "https://example.com/movie3"},
    ]

def youtube_search(query: str, max_results=3):
    # Dummy YouTube search result
    return [{"url": f"https://youtube.com/watch?v=dQw4w9WgXcQ&search={query}"}] * max_results

# --- Message Handler Endpoint ---
@app.route('/message', methods=['POST'])
def handle_message():
    data = request.json
    phone = data.get("phone")
    name = data.get("name", "Unknown")
    message = data.get("message", "")

    # Auto-save contact if new
    save_contact(phone, name)

    # Abuse detection
    abuse_msg = detect_abuse(phone, message)
    if abuse_msg:
        return jsonify({"reply": abuse_msg}), 200

    # Command: /search <query> - Free for all users
    if message.lower().startswith("/search "):
        query = message[len("/search "):].strip()
        movies = aggregate_search(query, os.getenv("TMDB_API_KEY", ""))
        trailers = youtube_search(query)

        replies = []
        for movie, trailer in zip(movies[:3], trailers):
            short = shorten_link(movie['link'])
            replies.append(f"🎥 *{movie.get('title', 'No Title')}*\n🔗 {short}\n🎬 Trailer: {trailer['url']}")

        save_activity(phone, "search", {"query": query})
        return jsonify({"reply": "\n\n".join(replies) if replies else "🙁 No results found."}), 200

    # Default reply if no command matched
    return jsonify({"reply": "🤖 Command not recognized. Use /search <movie name> to find movies."}), 200

if __name__ == "__main__":
    app.run(debug=True)

# premium_user_model.py

from pymongo import MongoClient
from config import MONGO_URI

client = MongoClient(MONGO_URI)
db = client["strangemind_ai"]
premium_collection = db["premium_users"]

def is_premium_user(user_id: str) -> bool:
    return premium_collection.find_one({"user_id": user_id}) is not None

def grant_premium(user_id: str):
    premium_collection.update_one(
        {"user_id": user_id},
        {"$set": {"status": "active"}},
        upsert=True
    )

def revoke_premium(user_id: str):
    premium_collection.delete_one({"user_id": user_id})

def list_all_premium_users():
    return premium_collection.find()
