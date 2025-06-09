from pymongo import MongoClient
import os
import openai

# --- MongoDB Setup ---
MONGO_URI = os.getenv("MONGO_URI")
client = MongoClient(MONGO_URI)
db = client.strangemindDB

vault_locks_collection = db.vault_locks
withdraw_locks_collection = db.withdraw_locks
vault_collection = db.vault_collection        # your main vault user data
global_settings_collection = db.global_settings_collection  # for global settings like withdraw locks

# --- OpenAI Setup ---
openai.api_key = os.getenv("OPENAI_API_KEY")

# --- Utils imports ---
from utils.helpers import is_admin
from utils.your_user_collections import users_collection, groups_collection
from utils.logging import log_activity

# --- Vault Lock Controls ---
def lock_vault(target: str):
    vault_locks_collection.update_one({"target": target}, {"$set": {"locked": True}}, upsert=True)

def unlock_vault(target: str):
    vault_locks_collection.update_one({"target": target}, {"$set": {"locked": False}}, upsert=True)

def is_vault_locked(target: str) -> bool:
    lock = vault_locks_collection.find_one({"target": target})
    return lock and lock.get("locked", False)

# --- Withdraw Lock Controls ---
def lock_withdraw(target: str):
    withdraw_locks_collection.update_one({"target": target}, {"$set": {"locked": True}}, upsert=True)

def unlock_withdraw(target: str):
    withdraw_locks_collection.update_one({"target": target}, {"$set": {"locked": False}}, upsert=True)

def is_withdraw_locked(target: str) -> bool:
    lock = withdraw_locks_collection.find_one({"target": target})
    return lock and lock.get("locked", False)

# --- Global Withdraw Lock Toggle ---
def set_global_withdraw_lock(lock: bool):
    global_settings_collection.update_one({"setting": "withdrawal_lock"}, {"$set": {"value": lock}}, upsert=True)

def get_global_withdraw_lock() -> bool:
    setting = global_settings_collection.find_one({"setting": "withdrawal_lock"})
    return setting and setting.get("value", False)

# --- Admin Command Handler ---
def handle_admin_commands(phone: str, message: str, send_message, is_group=False, group_id=None):
    if not is_admin(phone):
        return  # Unauthorized access; silent fail or log if needed

    msg = message.strip()
    msg_lower = msg.lower()

    # Basic lock/unlock commands for vault and withdraw (target can be @user or @group)
    if msg_lower.startswith("lock vault "):
        target = msg.split()[-1]
        lock_vault(target)
        send_message(phone, f"🔒 Vault locked for {target}")
        return

    if msg_lower.startswith("unlock vault "):
        target = msg.split()[-1]
        unlock_vault(target)
        send_message(phone, f"🔓 Vault unlocked for {target}")
        return

    if msg_lower.startswith("lock withdraw "):
        target = msg.split()[-1]
        lock_withdraw(target)
        send_message(phone, f"🚫 Withdrawals locked for {target}")
        return

    if msg_lower.startswith("unlock withdraw "):
        target = msg.split()[-1]
        unlock_withdraw(target)
        send_message(phone, f"✅ Withdrawals unlocked for {target}")
        return

    # Global withdrawal lock/unlock commands - example: /withdrawlock or /withdrawunlock
    if msg_lower == "/withdrawlock":
        set_global_withdraw_lock(True)
        send_message(phone, "🚫 Global withdrawal is LOCKED.")
        return

    if msg_lower == "/withdrawunlock":
        set_global_withdraw_lock(False)
        send_message(phone, "✅ Global withdrawals are UNLOCKED.")
        return

    # Stats command for quick DB insights
    if msg_lower == "stats":
        total_users = users_collection.count_documents({})
        total_groups = groups_collection.count_documents({})
        send_message(phone, f"📊 Total users: {total_users}\n📊 Total groups: {total_groups}")
        return

    # Fallback to OpenAI GPT-4 for admin questions or complex commands
    try:
        response = openai.ChatCompletion.create(
            model="gpt-4",
            messages=[
                {"role": "system", "content": (
                    "You are Strangemind AI’s assistant for admin users only. Keep it brief and professional."
                )},
                {"role": "user", "content": msg}
            ]
        )
        reply = response["choices"][0]["message"]["content"]
        send_message(phone, reply)
        log_activity(phone, "openai_response", msg)

    except Exception as e:
        send_message(phone, f"❌ OpenAI error: {str(e)}")

# --- Check Lock Status for User or Group ---
def check_lock_status(phone: str, group_id: str = None):
    # Check vault locks
    if is_vault_locked(phone) or (group_id and is_vault_locked(group_id)):
        return "🔒 Vault access is currently locked. Please contact admin."

    # Check withdraw locks (both user, group, and global)
    if is_withdraw_locked(phone) or (group_id and is_withdraw_locked(group_id)) or get_global_withdraw_lock():
        return "🚫 Withdrawals are currently locked. Please contact admin."

    return None

# Usage in your message processing pipeline:
# response = handle_admin_commands(phone, message, send_message, is_group, group_id)
# if response is not None:
#     return
# lock_message = check_lock_status(phone, group_id)
# if lock_message:
#     send_message(phone, lock_message)
#     return
