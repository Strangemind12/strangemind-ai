from utils import shorten_link, save_contact, save_activity
import os
from flask import Flask, request, jsonify
from datetime import datetime, timedelta
from pymongo import MongoClient

from scraper import aggregate_search, youtube_search
from utils import shorten_link, is_admin, get_vault_balance, withdraw_from_vault, send_whatsapp_message
from config import MONGO_URI, ADMIN_PHONE, NIGERIA_MONTHLY_PRICE
from premium_user_model import is_premium, create_premium_user
from abuse_detection import is_spammy

# Import your referral functions here:
from referral import create_referral, get_my_referral_code, get_referral_rankings, get_referrer_info

app = Flask(__name__)

# === DB Setup ===
client = MongoClient(MONGO_URI)
db = client.strangemindDB
users_collection = db.contacts
vault_collection = db.vault

ADMIN_PHONE = ADMIN_PHONE.strip()

def send_message(to_phone: str, message: str):
    # Replace with your actual send function
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

def handle_admin_command(message, phone):
    # Your admin command handler logic here, return a response string
    # Example placeholder:
    return "Admin command received."

@app.route('/webhook', methods=['POST'])
def webhook():
    data = request.json
    phone = data.get('from')
    message = data.get('text', '').strip()
    is_group = data.get('isGroup', False)
    mentions_bot = False

    # Check if message exists
    if not message:
        return jsonify({"status": "empty message"}), 400

    # Spam filtering
    if is_spammy(message):
        send_message(phone, "🚫 Spam detected. Message blocked.")
        return jsonify({"status": "blocked", "reason": "spam detected"}), 403

    # Detect if bot is mentioned in group chat
    if is_group and 'mentions' in data:
        mentions = data['mentions']  # list of mentioned phone numbers or IDs
        bot_phone = os.getenv("BOT_PHONE")
        mentions_bot = bot_phone in mentions

    # GROUP CHAT LOGIC
    if is_group:
        # Ignore if not a command or not mentioning bot
        if not (mentions_bot or message.startswith("/")):
            return jsonify({"status": "ignored"}), 200

        # Clean message if bot mentioned
        if mentions_bot:
            message = message.replace(f"@StrangemindAI", "").strip()

        # Admin commands
        admin_commands = ["/grant", "/revoke", "/vaultbalance", "/withdraw", "/checkpremium"]
        if any(message.lower().startswith(cmd) for cmd in admin_commands):
            if is_admin(phone):
                response = handle_admin_command(message, phone)
                send_message(phone, response)
                return jsonify({"status": "admin command processed"}), 200
            else:
                send_message(phone, "⛔ You are not authorized to perform admin actions.")
                return jsonify({"status": "unauthorized admin command"}), 403

        # REFERRAL COMMANDS (Group)
        if message.lower().startswith("/refer "):
            ref_code = message[len("/refer "):].strip()
            response = create_referral(phone, ref_code)
            send_message(phone, response)
            return jsonify({"status": "referral processed"}), 200

        if message.lower() == "/refer":
            response = get_my_referral_code(phone)
            send_message(phone, response)
            return jsonify({"status": "referral code shared"}), 200

        if message.lower() == "/referred":
            response = get_referrer_info(phone)
            send_message(phone, response)
            return jsonify({"status": "referrer info"}), 200

        if message.lower() == "/rank":
            response = get_referral_rankings()
            send_message(phone, response)
            return jsonify({"status": "referral rankings"}), 200

        # /movie command
        if message.lower().startswith("/movie "):
            query = message[len("/movie "):].strip()
            handle_movie_command(phone, query)
            return jsonify({"status": "movie command processed"}), 200

        # /search command (premium gated)
        if message.lower().startswith("/search "):
            if not check_premium(phone):
                send_message(phone, "⚠️ Premium access required. Subscribe to unlock this feature.")
                return jsonify({"status": "premium required"}), 200

            query = message[len("/search "):].strip()
            movies = aggregate_search(query, os.getenv("TMDB_API_KEY"))
            trailers = youtube_search(query)

            replies = []
            for movie, trailer in zip(movies[:3], trailers):
                short_link = shorten_link(movie['link'])
                replies.append(f"🎥 *{movie.get('title', 'No Title')}*\n🔗 {short_link}\n🎬 Trailer: {trailer['url']}")

            send_message(phone, "\n\n".join(replies) if replies else "🙁 No results found.")
            return jsonify({"status": "search command processed"}), 200

        # If mentioned but no command, escalate to admin
        if mentions_bot and message and not message.startswith("/"):
            escalation_message = (
                f"👤 User {phone} mentioned the bot with:\n\"{message}\"\n"
                f"🤖 AI cannot handle this. Admin intervention required."
            )
            send_message(os.getenv("ADMIN_PHONE"), escalation_message)
            send_message(phone, "⚠️ Your request has been forwarded to an admin for assistance.")
            return jsonify({"status": "escalated to admin"}), 200

        # Mentioned but empty message (help prompt)
        if mentions_bot and not message:
            send_message(phone, "🤖 Hi! Use `/movie movie name` or `/search movie name` to get movie info and trailers.")
            return jsonify({"status": "help prompt sent"}), 200

        return jsonify({"status": "ignored"}), 200

    # DIRECT MESSAGE LOGIC (non-group)

    # REFERRAL COMMANDS (DM)
    if message.lower().startswith("/refer "):
        ref_code = message[len("/refer "):].strip()
        response = create_referral(phone, ref_code)
        send_message(phone, response)
        return jsonify({"status": "referral processed"}), 200

    if message.lower() == "/refer":
        response = get_my_referral_code(phone)
        send_message(phone, response)
        return jsonify({"status": "referral code shared"}), 200

    if message.lower() == "/referred":
        response = get_referrer_info(phone)
        send_message(phone, response)
        return jsonify({"status": "referrer info"}), 200

    if message.lower() == "/rank":
        response = get_referral_rankings()
        send_message(phone, response)
        return jsonify({"status": "referral rankings"}), 200

    # /movie command (DM)
    if message.lower().startswith("/movie "):
        query = message[len("/movie "):].strip()
        if not check_premium(phone):
            send_message(phone, "⚠️ Your premium is inactive. Subscribe to unlock movie features.")
            return jsonify({"status": "premium required"}), 200
        handle_movie_command(phone, query)
        return jsonify({"status": "movie command processed"}), 200

    # /search command (premium gated DM)
    if message.lower().startswith("/search "):
        if not check_premium(phone):
            send_message(phone, "⚠️ Your premium is inactive. Subscribe to unlock full features.")
            return jsonify({"status": "premium required"}), 200

        query = message[len("/search "):].strip()
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

    # For any other message, send help prompt
    send_message(phone, "📽 Send `/search movie name` or `/movie movie name` to get links + trailers!")
    return jsonify({"status": "idle"}), 200

if __name__ == '__main__':
    app.run(debug=True, port=int(os.getenv("PORT", 5000)))
