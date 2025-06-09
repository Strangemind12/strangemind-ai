from utils import chimoney_client, walletsafrica_client from database import global_settings_collection, users_collection from utils.logging import log_activity import time import os import requests

In-memory cooldown tracker (replace with Redis in production)

cooldown_tracker = {}

─── MAIN COMMAND HANDLER ─────────────────────────────────────────

def handle_wallet_commands(phone, message): message = message.strip().lower() tokens = message.split()

if not tokens:
    return "❓ Invalid command. Try /balance or /withdraw <amount>"

cmd = tokens[0]

# ─── Admin Commands ──────────
admin_response = handle_admin_wallet_control(phone, cmd)
if admin_response:
    return admin_response

# ─── Global Lock Check ───────
if is_withdraw_locked():
    return "🚫 Withdrawals are currently locked by admin."

# ─── /balance ────────────────
if cmd == "/balance":
    wallet_id = get_user_wallet_id(phone)
    currency = get_user_currency(phone) or "NGN"

    chimoney_balance = chimoney_client.get_balance(wallet_id)
    if chimoney_balance:
        return f"💼 Your Chimoney balance: {chimoney_balance['balance']} {chimoney_balance['currency']}"

    wallets_balance = walletsafrica_client.get_balance(wallet_id)
    if wallets_balance:
        return f"💼 Your Wallets Africa balance: {wallets_balance['balance']} {wallets_balance['currency']}"

    return "⚠️ Unable to fetch your balance from any provider."

# ─── /withdraw <amount> ─────
elif cmd == "/withdraw":
    if len(tokens) != 2 or not tokens[1].isdigit():
        return "⚠️ Usage: /withdraw 500"

    amount = int(tokens[1])
    if amount < 100:
        return "❌ Minimum withdrawal is ₦100."

    if is_on_cooldown(phone):
        return "🕒 Please wait before requesting another withdrawal."

    wallet_id = get_user_wallet_id(phone)
    currency = get_user_currency(phone) or "NGN"
    recipient = get_user_payout_account(phone)

    try:
        tx = chimoney_client.send_funds(wallet_id, amount, currency, recipient=recipient)
        if tx and tx.get("transaction_id"):
            log_activity(phone, "wallet_withdraw", f"Chimoney: {amount} {currency}")
            return f"✅ Withdrawal of ₦{amount} initiated via Chimoney. TXID: {tx['transaction_id']}"
    except Exception as e:
        print("Chimoney error:", e)

    try:
        tx = walletsafrica_client.send_funds(wallet_id, amount, currency, recipient=recipient)
        if tx and tx.get("transaction_id"):
            log_activity(phone, "wallet_withdraw", f"WalletsAfrica: {amount} {currency}")
            return f"✅ Withdrawal of ₦{amount} processed via Wallets Africa. TXID: {tx['transaction_id']}"
    except Exception as e:
        print("WalletsAfrica error:", e)

    return (
        "❌ Withdrawal failed. We tried Chimoney and Wallets Africa but both returned errors.\n"
        "Please try again later or contact support if the issue persists."
    )

return None

─── ADMIN COMMANDS ────────────────────────────────────────────────

ADMIN_NUMBERS = ["2348012345678", "2349087654321"]  # Update with your real numbers

def handle_admin_wallet_control(phone, command): if phone not in ADMIN_NUMBERS: return None

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

─── HELPERS ───────────────────────────────────────────────────────

def get_user_wallet_id(phone): user = users_collection.find_one({"phone": phone}) return user.get("wallet_id", "default_wallet_id")

def get_user_currency(phone): user = users_collection.find_one({"phone": phone}) return user.get("currency", "NGN")

def get_user_payout_account(phone): user = users_collection.find_one({"phone": phone}) return user.get("payout_account", "default_payout@example.com")

def is_withdraw_locked(): setting = global_settings_collection.find_one({"setting": "withdrawal_lock"}) return setting.get("value", False)

def is_on_cooldown(phone): now = time.time() last = cooldown_tracker.get(phone) if last and (now - last) < 30: return True cooldown_tracker[phone] = now return False

------------------ Chimoney Setup ------------------

CHIMONEY_API_KEY = os.getenv("CHIMONEY_API_KEY") CHIMONEY_API_SECRET = os.getenv("CHIMONEY_API_SECRET") CHIMONEY_BASE_URL = "https://api.chimoney.io/v1"

CHIMONEY_HEADERS = { "x-api-key": CHIMONEY_API_KEY, "Authorization": f"Bearer {CHIMONEY_API_SECRET}", "Content-Type": "application/json" }

def chimoney_get_balance(wallet_id): url = f"{CHIMONEY_BASE_URL}/wallets/{wallet_id}/balance" try: response = requests.get(url, headers=CHIMONEY_HEADERS) if response.ok: return response.json() except Exception as e: print(f"[Chimoney Balance Error]: {e}") return None

def chimoney_send_funds(wallet_id, amount, currency, recipient): url = f"{CHIMONEY_BASE_URL}/wallets/{wallet_id}/send" payload = { "amount": amount, "currency": currency, "recipient": recipient } try: response = requests.post(url, json=payload, headers=CHIMONEY_HEADERS) if response.ok: return response.json() except Exception as e: print(f"[Chimoney Transfer Error]: {e}") return None

------------------ WalletsAfrica Setup ------------------

WALLETSAFRICA_API_KEY = os.getenv("WALLETSAFRICA_API_KEY") WALLETSAFRICA_API_SECRET = os.getenv("WALLETSAFRICA_API_SECRET") WALLETSAFRICA_BASE_URL = "https://api.wallets.africa/v1"

WALLETSAFRICA_HEADERS = { "x-api-key": WALLETSAFRICA_API_KEY, "Authorization": f"Bearer {WALLETSAFRICA_API_SECRET}", "Content-Type": "application/json" }

def walletsafrica_get_balance(account_id): url = f"{WALLETSAFRICA_BASE_URL}/accounts/{account_id}/balance" try: response = requests.get(url, headers=WALLETSAFRICA_HEADERS) if response.ok: return response.json() except Exception as e: print(f"[WalletsAfrica Balance Error]: {e}") return None

def walletsafrica_send_funds(account_id, amount, currency, recipient_account): url = f"{WALLETSAFRICA_BASE_URL}/transfers" payload = { "account_id": account_id, "amount": amount, "currency": currency, "recipient_account": recipient_account } try: response = requests.post(url, json=payload, headers=WALLETSAFRICA_HEADERS) if response.ok: return response.json() except Exception as e: print(f"[WalletsAfrica Transfer Error]: {e}") return None

