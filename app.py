import os
from flask import Flask, request, jsonify
from datetime import datetime, timedelta
from pymongo import MongoClient
from scraper import aggregate_search
from utils import shorten_link, youtube_search, is_premium_user, is_admin, get_vault_balance, withdraw_from_vault
from config import MONGO_URI, ADMIN_PHONE, NIGERIA_MONTHLY_PRICE

app = Flask(__name__)

# === DB Setup ===
client = MongoClient(MONGO_URI)
db = client.strangemindDB
users_collection = db.contacts
vault_collection = db.vault

# === Helper functions ===

def send_message(to_phone: str, message: str):
    # Hook your WhatsApp or Gupshup API here
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

# === Routes ===

@app.route('/search', methods=['GET'])
def search_movie_api():
    query = request.args.get('query')
    phone = request.args.get('phone')  # for premium check

    if not query:
        return jsonify({"error": "Missing 'query' parameter"}), 400

    is_premium = phone and check_premium(phone)  # use your own premium check, not utils.is_premium_user

    raw_results = aggregate_search(query, os.getenv("TMDB_API_KEY"))
    monetized_results = [
        {
            "title": item.get('title', 'No Title'),
            "link": shorten_link(item['link']),
            "source": item.get('source', 'Unknown')
        }
        for item in raw_results
    ]

    trailers = youtube_search(query) if is_premium else []

    return jsonify({
        "status": "success",
        "premium_user": bool(is_premium),
        "movies": monetized_results,
        "trailers": trailers if is_premium else "Upgrade to premium to view trailers 🎥"
    })

@app.route('/vault/balance', methods=['GET'])
def vault_balance():
    phone = request.args.get('phone')
    if not phone or not is_admin(phone):
        return jsonify({"error": "Unauthorized or missing phone parameter"}), 403
    balance = get_vault_balance()
    return jsonify({"vault_balance": balance})

@app.route('/vault/withdraw', methods=['POST'])
def vault_withdraw():
    data = request.json
    phone = data.get('phone')
    amount = data.get('amount')
    if not phone or not is_admin(phone):
        return jsonify({"error": "Unauthorized"}), 403
    if not amount or amount <= 0:
        return jsonify({"error": "Invalid amount"}), 400
    success = withdraw_from_vault(amount)
    if not success:
        return jsonify({"error": "Insufficient balance"}), 400
    return jsonify({"message": f"Successfully withdrew {amount} units from vault."})

@app.route('/webhook', methods=['POST'])
def webhook():
    data = request.json
    phone = data.get('from')
    message = data.get('text', '').strip()
    is_group = data.get('isGroup', False)

    if not message:
        return jsonify({"status": "empty message"}), 400

    if message.startswith("/"):
        # Admin or user commands
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

        # Otherwise, assume admin command
        response = handle_admin_command(message, phone)
        send_message(phone, response)
        return jsonify({"status": "command processed"}), 200

    # Default message
    send_message(phone, "📽 Send `/search movie name` to get links + trailers!")
    return jsonify({"status": "idle"}), 200

@app.route('/payment-webhook', methods=['POST'])
def payment_webhook():
    data = request.json
    phone = data.get('customer_phone')
    amount = float(data.get('amount', 0))
    status = data.get('status')

    if status != "successful":
        return jsonify({"status": "ignored"}), 200

    if amount >= NIGERIA_MONTHLY_PRICE:
        expiry = grant_premium(phone, 30)
        send_message(phone, f"✅ Premium activated! Valid till {expiry.strftime('%Y-%m-%d')}")
        return jsonify({"status": "premium granted"}), 200

    return jsonify({"error": "Insufficient payment"}), 400


# === Admin command handler (kept from your original) ===
def handle_admin_command(command_text: str, sender_phone: str) -> str:
    parts = command_text.strip().split()
    command = parts[0].lower()

    if not is_admin(sender_phone):
        return "⛔ You are not authorized to perform admin actions."

    if command == "/grant" and len(parts) >= 2:
        target_phone = parts[1]
        days = int(parts[2]) if len(parts) == 3 else 30
        expiry = grant_premium(target_phone, days)
        return f"✅ Premium granted to {target_phone} until {expiry.strftime('%Y-%m-%d')}."

    if command == "/revoke" and len(parts) == 2:
        revoke_premium(parts[1])
        return f"❌ Premium revoked from {parts[1]}."

    if command == "/checkpremium" and len(parts) == 2:
        status = check_premium(parts[1])
        return f"🔍 Premium status for {parts[1]}: {'✅ ACTIVE' if status else '❌ INACTIVE'}."

    if command == "/vaultbalance":
        return f"💰 Vault balance: ₦{get_vault_balance()}"

    if command == "/withdraw" and len(parts) == 2:
        try:
            amount = float(parts[1])
        except ValueError:
            return "❌ Invalid amount format."
        return f"💸 ₦{amount} withdrawn." if withdraw_from_vault(amount) else "❌ Insufficient vault balance."

    return "❓ Unknown admin command."


# === App Start ===
if __name__ == '__main__':
    port = int(os.getenv('PORT', 5000))
    app.run(host='0.0.0.0', port=port)
