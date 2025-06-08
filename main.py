# main.py
import os
from flask import Flask, request, jsonify
from datetime import datetime, timedelta
from pymongo import MongoClient
from config import MONGO_URI, ADMIN_PHONE, NIGERIA_MONTHLY_PRICE

app = Flask(__name__)

# MongoDB setup
client = MongoClient(MONGO_URI)
db = client.strangemindDB
users_collection = db.contacts
vault_collection = db.vault

ADMIN_PHONE = ADMIN_PHONE

# === UTILS ===
def send_message(to_phone: str, message: str):
    # Hook up your WhatsApp or Gupshup API here
    print(f"[Message -> {to_phone}]: {message}")

# === PREMIUM LOGIC ===
def is_admin(phone: str) -> bool:
    return phone == ADMIN_PHONE

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
    return True

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

def get_vault_balance():
    vault = vault_collection.find_one({"admin": ADMIN_PHONE})
    return vault.get("balance", 0) if vault else 0

def withdraw_from_vault(amount: float) -> bool:
    vault = vault_collection.find_one({"admin": ADMIN_PHONE})
    if not vault or vault.get("balance", 0) < amount:
        return False
    vault_collection.update_one(
        {"admin": ADMIN_PHONE},
        {"$inc": {"balance": -amount}}
    )
    return True

# === COMMAND HANDLER ===
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
        target_phone = parts[1]
        revoke_premium(target_phone)
        return f"❌ Premium revoked from {target_phone}."

    if command == "/checkpremium" and len(parts) == 2:
        target_phone = parts[1]
        status = check_premium(target_phone)
        return f"🔍 Premium status for {target_phone}: {'✅ ACTIVE' if status else '❌ INACTIVE'}."

    if command == "/vaultbalance":
        balance = get_vault_balance()
        return f"💰 Vault balance: ₦{balance}"

    if command == "/withdraw" and len(parts) == 2:
        try:
            amount = float(parts[1])
        except ValueError:
            return "❌ Invalid amount format."
        if withdraw_from_vault(amount):
            return f"💸 ₦{amount} withdrawn from vault."
        else:
            return "❌ Insufficient vault balance."

    return "❓ Unknown admin command."

# === MESSAGE HANDLER ===
@app.route('/webhook', methods=['POST'])
def webhook():
    data = request.json
    phone = data.get('from')
    message = data.get('text')
    is_group = data.get('isGroup', False)
    group_id = data.get('groupId') if is_group else None

    # Admin commands
    if message and message.startswith("/"):
        response = handle_admin_command(message, phone)
        send_message(phone, response)
        return jsonify({"status": "command processed"}), 200

    # Check premium status for user
    if not check_premium(phone):
        send_message(phone, "⚠️ Your premium subscription is inactive or expired. Please subscribe to enjoy full features.")
        return jsonify({"status": "premium expired"}), 200

    # Handle normal message (you can extend this)
    send_message(phone, f"👋 Hey {phone}, your message was received and you have premium access!")

    return jsonify({"status": "success"}), 200

# === PAYMENT WEBHOOK ===
@app.route('/payment-webhook', methods=['POST'])
def payment_webhook():
    data = request.json
    payer_phone = data.get('customer_phone')
    amount = float(data.get('amount', 0))
    payment_status = data.get('status')

    if payment_status != "successful":
        return jsonify({"status": "ignored"}), 200

    if amount >= NIGERIA_MONTHLY_PRICE:
        expiry_date = grant_premium(payer_phone, days=30)
        send_message(payer_phone, f"✅ Premium activated! Subscription valid until {expiry_date.strftime('%Y-%m-%d')}")
        return jsonify({"status": "success"}), 200
    else:
        return jsonify({"error": "Insufficient payment"}), 400

if __name__ == '__main__':
    port = int(os.getenv('PORT', 5000))
    app.run(host='0.0.0.0', port=port)
