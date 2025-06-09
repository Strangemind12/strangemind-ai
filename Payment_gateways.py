# app.py
from flask import Flask, request, jsonify
from pymongo import MongoClient, ReturnDocument
import os
import re
import time
import logging

app = Flask(__name__)
logging.basicConfig(level=logging.INFO)

MONGO_URI = os.getenv("MONGO_URI")
client = MongoClient(MONGO_URI)
db = client.strangemindDB
transactions_collection = db.transactions
users_collection = db.users
global_settings_collection = db.global_settings
cooldown_collection = db.cooldowns  # New collection for cooldowns

PHONE_REGEX = re.compile(r"^\+?234\d{10}$")  # Nigerian phone format with optional +

# Helper function to validate phone
def validate_phone(phone):
    if not phone:
        return False
    phone = phone.strip()
    # Ensure phone starts with +234 or 234 and is followed by 10 digits
    if not PHONE_REGEX.match(phone):
        return False
    return True

@app.route("/webhook/payment-status", methods=["POST"])
def payment_status():
    data = request.json or {}
    transaction_id = data.get("transaction_id")
    status = data.get("status")
    phone = data.get("user_phone")
    timestamp = data.get("timestamp")

    if not transaction_id or not status or not phone:
        return jsonify({"error": "Missing required fields"}), 400

    if not validate_phone(phone):
        return jsonify({"error": "Invalid phone format"}), 400

    # Validate status against allowed statuses (example)
    allowed_statuses = {"pending", "completed", "failed", "cancelled"}
    if status not in allowed_statuses:
        return jsonify({"error": f"Invalid status '{status}'"}), 400

    transactions_collection.update_one(
        {"transaction_id": transaction_id},
        {"$set": {"status": status, "timestamp": timestamp}},
        upsert=True,
    )

    logging.info(f"Updated transaction {transaction_id} with status {status}")

    # TODO: Notify user/admin here asynchronously if needed

    return jsonify({"message": "Webhook received"}), 200


# ------------- Cooldown functions using MongoDB -------------
COOLDOWN_SECONDS = 30

def is_on_cooldown(phone):
    now = time.time()
    doc = cooldown_collection.find_one({"phone": phone})
    if doc:
        last_time = doc.get("last_request_time", 0)
        if now - last_time < COOLDOWN_SECONDS:
            return True
    # Update cooldown
    cooldown_collection.find_one_and_update(
        {"phone": phone},
        {"$set": {"last_request_time": now}},
        upsert=True
    )
    return False


# ---------- Cached user fetch with TTL (simple in-memory) --------
# This cache lives only as long as the app runs; good enough for small scale
_user_cache = {}
CACHE_TTL = 60  # seconds

def get_user(phone):
    now = time.time()
    cached = _user_cache.get(phone)
    if cached and (now - cached['timestamp']) < CACHE_TTL:
        return cached['user']
    user = users_collection.find_one({"phone": phone})
    if user:
        _user_cache[phone] = {"user": user, "timestamp": now}
    return user


# ----------- Main Wallet Command Handler ----------------
import requests
from utils.logging import log_activity

CHIMONEY_API_KEY = os.getenv("CHIMONEY_API_KEY")
CHIMONEY_API_SECRET = os.getenv("CHIMONEY_API_SECRET")
CHIMONEY_BASE_URL = "https://api.chimoney.io/v1"
CHIMONEY_HEADERS = {
    "x-api-key": CHIMONEY_API_KEY,
    "Authorization": f"Bearer {CHIMONEY_API_SECRET}",
    "Content-Type": "application/json"
}

WALLETSAFRICA_API_KEY = os.getenv("WALLETSAFRICA_API_KEY")
WALLETSAFRICA_API_SECRET = os.getenv("WALLETSAFRICA_API_SECRET")
WALLETSAFRICA_BASE_URL = "https://api.wallets.africa/v1"
WALLETSAFRICA_HEADERS = {
    "x-api-key": WALLETSAFRICA_API_KEY,
    "Authorization": f"Bearer {WALLETSAFRICA_API_SECRET}",
    "Content-Type": "application/json"
}

ADMIN_NUMBERS = ["+2348012345678", "+2349087654321"]  # Normalize with + sign

def get_user_wallet_id(phone):
    user = get_user(phone)
    return user.get("wallet_id") if user else None

def get_user_currency(phone):
    user = get_user(phone)
    return user.get("currency", "NGN") if user else "NGN"

def get_user_payout_account(phone):
    user = get_user(phone)
    return user.get("payout_account") if user else None

def is_withdraw_locked():
    setting = global_settings_collection.find_one({"setting": "withdrawal_lock"})
    return setting.get("value", False) if setting else False


def chimoney_get_balance(wallet_id):
    url = f"{CHIMONEY_BASE_URL}/wallets/{wallet_id}/balance"
    try:
        response = requests.get(url, headers=CHIMONEY_HEADERS, timeout=5)
        if response.ok:
            return response.json()
        logging.error(f"Chimoney get_balance failed: {response.text}")
    except Exception as e:
        logging.error(f"[Chimoney Balance Error]: {e}")
    return None

def chimoney_send_funds(wallet_id, amount, currency, recipient):
    url = f"{CHIMONEY_BASE_URL}/wallets/{wallet_id}/send"
    payload = {"amount": amount, "currency": currency, "recipient": recipient}
    try:
        response = requests.post(url, json=payload, headers=CHIMONEY_HEADERS, timeout=5)
        if response.ok:
            return response.json()
        logging.error(f"Chimoney send_funds failed: {response.text}")
    except Exception as e:
        logging.error(f"[Chimoney Transfer Error]: {e}")
    return None

def walletsafrica_get_balance(account_id):
    url = f"{WALLETSAFRICA_BASE_URL}/accounts/{account_id}/balance"
    try:
        response = requests.get(url, headers=WALLETSAFRICA_HEADERS, timeout=5)
        if response.ok:
            return response.json()
        logging.error(f"WalletsAfrica get_balance failed: {response.text}")
    except Exception as e:
        logging.error(f"[WalletsAfrica Balance Error]: {e}")
    return None

def walletsafrica_send_funds(account_id, amount, currency, recipient_account):
    url = f"{WALLETSAFRICA_BASE_URL}/transfers"
    payload = {
        "account_id": account_id,
        "amount": amount,
        "currency": currency,
        "recipient_account": recipient_account
    }
    try:
        response = requests.post(url, json=payload, headers=WALLETSAFRICA_HEADERS, timeout=5)
        if response.ok:
            return response.json()
        logging.error(f"WalletsAfrica send_funds failed: {response.text}")
    except Exception as e:
        logging.error(f"[WalletsAfrica Transfer Error]: {e}")
    return None


def handle_admin_wallet_control(phone, command):
    if phone not in ADMIN_NUMBERS:
        return None

    if command == "/withdrawlock":
        global_settings_collection.update_one(
            {"setting": "withdrawal_lock"},
            {"$set": {"value": True}},
            upsert=True
        )
        return "🔒 Withdrawals have been locked."

    if command == "/withdrawunlock":
        global_settings_collection.update_one(
            {"setting": "withdrawal_lock"},
            {"$set": {"value": False}},
            upsert=True
        )
        return "🔓 Withdrawals have been unlocked."

    return None

def handle_wallet_commands(phone, message):
    message = message.strip().lower()
    tokens = message.split()

    if not tokens:
        return "❓ Invalid command. Try /balance or /withdraw <amount>"

    cmd = tokens[0]

    # Admin commands
    admin_response = handle_admin_wallet_control(phone, cmd)
    if admin_response:
        return admin_response

    # Global withdrawal lock check
    if is_withdraw_locked():
        return "🚫 Withdrawals are currently locked by admin."

    if cmd == "/balance":
        wallet_id = get_user_wallet_id(phone)
        if not wallet_id:
            return "⚠️ Wallet ID not found for your account."

        currency = get_user_currency(phone) or "NGN"

        chimoney_balance = chimoney_get_balance(wallet_id)
        if chimoney_balance:
            balance = chimoney_balance.get("balance")
            curr = chimoney_balance.get("currency", currency)
            return f"💼 Your Chimoney balance: {balance} {curr}"

        wallets_balance = walletsafrica_get_balance(wallet_id)
        if wallets_balance:
            balance = wallets_balance.get("balance")
            curr = wallets_balance.get("currency", currency)
            return f"💼 Your Wallets Africa balance: {balance} {curr}"

        return "⚠️ Unable to fetch your balance from any provider."

    elif cmd == "/withdraw":
        if len(tokens) != 2:
            return "⚠️ Usage: /withdraw <amount>"

        try:
            amount = int(tokens[1])
        except ValueError:
            return "❌ Invalid amount. Please enter a whole number."

        if amount < 100:
            return "❌ Minimum withdrawal is ₦100."

        if is_on_cooldown(phone):
            return f"🕒 Please wait {COOLDOWN_SECONDS} seconds before requesting another withdrawal."

        wallet_id = get_user_wallet_id(phone)
        if not wallet_id:
            return "⚠️ Wallet ID not found for your account."

        currency = get_user_currency(phone) or "NGN"
        recipient = get_user_payout_account(phone)
        if not recipient:
            return "⚠️ Payout account not configured."

        # Try Chimoney
        tx = chimoney_send_funds(wallet_id, amount, currency, recipient)
        if tx and tx.get("transaction_id"):
            log_activity(phone, "wallet_withdraw", f"Chimoney: {amount} {currency}")
            return f"✅ Withdrawal of ₦{amount} initiated via Chimoney. TXID: {tx['transaction_id']}"

        # Fallback Wallets Africa
        tx = walletsafrica_send_funds(wallet_id, amount, currency, recipient)
        if tx and tx.get("transaction_id"):
            log_activity(phone, "wallet_withdraw", f"WalletsAfrica: {amount} {currency}")
            return f"✅ Withdrawal of ₦{amount} processed via Wallets Africa. TXID: {tx['transaction_id']}"

        return (
            "❌ Withdrawal failed. Both Chimoney and Wallets Africa returned errors.\n"
            "Please try again later or contact support if the issue persists."
        )

    return "❓ Unknown command. Try /balance or /withdraw <amount>"

if __name__ == "__main__":
    # For production: Use gunicorn or similar WSGI server
    # gunicorn -w 4 -b 0.0.0.0:5001 app:app
    app.run(port=5001, debug=False)

from flask import Flask, request, jsonify
from pymongo import MongoClient
import os

app = Flask(__name__)

MONGO_URI = os.getenv("MONGO_URI")
client = MongoClient(MONGO_URI)
db = client.strangemindDB
transactions_collection = db.transactions

@app.route("/webhook/payment-status", methods=["POST"])
def payment_status():
    data = request.json
    transaction_id = data.get("transaction_id")
    status = data.get("status")
    phone = data.get("user_phone")

    if not transaction_id or not status or not phone:
        return jsonify({"error": "Invalid data"}), 400

    transactions_collection.update_one(
        {"transaction_id": transaction_id},
        {"$set": {"status": status, "timestamp": data.get("timestamp")}},
        upsert=True,
    )

    # Optionally notify user/admin

    return jsonify({"message": "Webhook received"}), 200

if __name__ == "__main__":
    app.run(port=5001)
