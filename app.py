import os
from flask import Flask, request, jsonify
from datetime import datetime, timedelta
from pymongo import MongoClient

from scraper import aggregate_search, youtube_search
from utils import shorten_link, is_admin, get_vault_balance, withdraw_from_vault, send_whatsapp_message
from config import MONGO_URI, ADMIN_PHONE, NIGERIA_MONTHLY_PRICE
from premium_user_model import is_premium, create_premium_user
from abuse_detection import is_spammy

app = Flask(__name__)

# === DB Setup ===
client = MongoClient(MONGO_URI)
db = client.strangemindDB
users_collection = db.contacts
vault_collection = db.vault

ADMIN_PHONE = ADMIN_PHONE.strip()

def send_message(to_phone: str, message: str):
    print(f"[Message to {to_phone}]: {message}")

def grant_premium(phone: str, days: int = 30):
    expiry_date = datetime.utcnow() + timedelta(days=days)
    users_collection.update_one(
        {"phone": phone},
        {"$set": {"is_premium": True, "premium_expiry": expiry_date}},
        upsert=True
    )
    vault_collection.update_one(
        {"admin": ADMIN_PHONE},
        {"$inc": {"balance": NIGERIA_MONTHLY_PRICE}},
        upsert=True
    )
    return expiry_date

def revoke_premium(phone: str):
    users_collection.update_one(
        {"phone": phone},
        {"$set": {"is_premium": False, "premium_expiry": None}}
    )

def check_premium(phone: str) -> bool:
    user = users_collection.find_one({"phone": phone})
    if not user:
        return False
    expiry = user.get("premium_expiry")
    if expiry and expiry > datetime.utcnow():
        return True
    if user.get("is_premium", False):
        revoke_premium(phone)
    return False

def handle_movie_command(user_phone, query):
    TMDB_API_KEY = os.getenv("TMDB_API_KEY")
    YOUTUBE_API_KEY = os.getenv("YOUTUBE_API_KEY")

    movie_results = aggregate_search(query, tmdb_api_key=TMDB_API_KEY)
    trailer_results = youtube_search(query, max_results=3, youtube_api_key=YOUTUBE_API_KEY)

    message = f"🎬 Results for \"{query}\":\n\n"
    for idx, movie in enumerate(movie_results[:5], 1):
        message += f"{idx}️⃣ {movie['title']}\nLink: {movie['link']}\nSource: {movie['source']}\n\n"

    if trailer_results:
        message += "🎥 YouTube Trailers:\n"
        for trailer in trailer_results:
            message += f"- {trailer['title']}: {trailer['url']}\n"

    send_whatsapp_message(user_phone, message)

def on_message_received(user_phone, message_text):
    if message_text.startswith("/movie "):
        query = message_text[len("/movie "):].strip()
        if not check_premium(user_phone):
            send_whatsapp_message(user_phone, "⚠️ Your premium is inactive. Subscribe to unlock movie features.")
            return
        handle_movie_command(user_phone, query)
    else:
        send_whatsapp_message(user_phone, "📽 Send `/movie movie name` to get movie links + trailers!")

@app.route('/webhook', methods=['POST'])
def webhook():
    data = request.json
    phone = data.get('from')
    message = data.get('text', '').strip()
    is_group = data.get('isGroup', False)

    if not message:
        return jsonify({"status": "empty message"}), 400

    if is_spammy(message):
        send_message(phone, "🚫 Spam detected. Message blocked.")
        return jsonify({"status": "blocked", "reason": "spam detected"}), 403

    # Check for /movie command using the new handler
    if message.lower().startswith("/movie "):
        on_message_received(phone, message)
        return jsonify({"status": "movie command processed"}), 200

    # Existing command logic for /search and admin commands
    if message.startswith("/"):
        if message.lower().startswith("/search "):
            if not check_premium(phone):
                send_message(phone, "⚠️ Your premium is inactive. Subscribe to unlock full features.")
                return jsonify({"status": "premium required"}), 200

            query = message[8:].strip()
            movies = aggregate_search(query, os.getenv("TMDB_API_KEY"))
            trailers = youtube_search(query)

            replies = []
            for movie, trailer in zip(movies[:3], trailers):
                short = shorten_link(movie['link'])
                replies.append(
                    f"🎥 *{movie.get('title', 'No Title')}*\n🔗 {short}\n🎬 Trailer: {trailer['url']}"
                )

            send_message(phone, "\n\n".join(replies) if replies else "🙁 No results found.")
            return jsonify({"status": "search processed"}), 200

        # Admin commands
        response = handle_admin_command(message, phone)
        send_message(phone, response)
        return jsonify({"status": "command processed"}), 200

    send_message(phone, "📽 Send `/search movie name` or `/movie movie name` to get links + trailers!")
    return jsonify({"status": "idle"}), 200

# ... rest of your routes and admin handlers ...

if __name__ == '__main__':
    app.run(debug=True, port=int(os.getenv("PORT", 5000)))
