from pymongo import MongoClient import os import openai

--- MongoDB Setup ---

MONGO_URI = os.getenv("MONGO_URI") client = MongoClient(MONGO_URI) db = client.strangemindDB

vault_locks_collection = db.vault_locks withdraw_locks_collection = db.withdraw_locks vault_collection = db.vault_collection        # your main vault user data global_settings_collection = db.global_settings_collection  # for global settings like withdraw locks

--- OpenAI Setup ---

openai.api_key = os.getenv("OPENAI_API_KEY")

--- Utils imports ---

from utils.helpers import is_admin from utils.your_user_collections import users_collection, groups_collection from utils.logging import log_activity

--- Vault Lock Controls ---

def lock_vault(target: str): vault_locks_collection.update_one({"target": target}, {"$set": {"locked": True}}, upsert=True)

def unlock_vault(target: str): vault_locks_collection.update_one({"target": target}, {"$set": {"locked": False}}, upsert=True)

def is_vault_locked(target: str) -> bool: lock = vault_locks_collection.find_one({"target": target}) return lock and lock.get("locked", False)

--- Withdraw Lock Controls ---

def lock_withdraw(target: str): withdraw_locks_collection.update_one({"target": target}, {"$set": {"locked": True}}, upsert=True)

def unlock_withdraw(target: str): withdraw_locks_collection.update_one({"target": target}, {"$set": {"locked": False}}, upsert=True)

def is_withdraw_locked(target: str) -> bool: lock = withdraw_locks_collection.find_one({"target": target}) return lock and lock.get("locked", False)

--- Global Withdraw Lock Toggle ---

def set_global_withdraw_lock(lock: bool): global_settings_collection.update_one({"setting": "withdrawal_lock"}, {"$set": {"value": lock}}, upsert=True)

def get_global_withdraw_lock() -> bool: setting = global_settings_collection.find_one({"setting": "withdrawal_lock"}) return setting and setting.get("value", False)

--- Admin Command Handler ---

def handle_admin_commands(phone: str, message: str, send_message, is_group=False, group_id=None): if not is_admin(phone): return  # Unauthorized access; silent fail or log if needed

msg = message.strip() msg_lower = msg.lower()

Basic lock/unlock commands for vault and withdraw (target can be @user or @group)

if msg_lower.startswith("lock vault "): target = msg.split()[-1] lock_vault(target) send_message(phone, f"🔒 Vault locked for {target}") return

if msg_lower.startswith("unlock vault "): target = msg.split()[-1] unlock_vault(target) send_message(phone, f"🔓 Vault unlocked for {target}") return

if msg_lower.startswith("lock withdraw "): target = msg.split()[-1] lock_withdraw(target) send_message(phone, f"🚫 Withdrawals locked for {target}") return

if msg_lower.startswith("unlock withdraw "): target = msg.split()[-1] unlock_withdraw(target) send_message(phone, f"✅ Withdrawals unlocked for {target}") return

Global withdrawal lock/unlock commands - example: /withdrawlock or /withdrawunlock

if msg_lower == "/withdrawlock": set_global_withdraw_lock(True) send_message(phone, "🚫 Global withdrawal is LOCKED.") return

if msg_lower == "/withdrawunlock": set_global_withdraw_lock(False) send_message(phone, "✅ Global withdrawals are UNLOCKED.") return

Stats command for quick DB insights

if msg_lower == "stats": total_users = users_collection.count_documents({}) total_groups = groups_collection.count_documents({}) send_message(phone, f"📊 Total users: {total_users}\n📊 Total groups: {total_groups}") return

Fallback to OpenAI GPT-4 for admin questions or complex commands

try: response = openai.ChatCompletion.create( model="gpt-4", messages=[ {"role": "system", "content": ( "You are Strangemind AI’s assistant for admin users only. Keep it brief and professional." )}, {"role": "user", "content": msg} ] ) reply = response["choices"][0]["message"]["content"] send_message(phone, reply) log_activity(phone, "openai_response", msg)

except Exception as e: send_message(phone, f"❌ OpenAI error: {str(e)}")

--- Check Lock Status for User or Group ---

def check_lock_status(phone: str, group_id: str = None): # Check vault locks if is_vault_locked(phone) or (group_id and is_vault_locked(group_id)): return "🔒 Vault access is currently locked. Please contact admin."

Check withdraw locks (both user, group, and global)

if is_withdraw_locked(phone) or (group_id and is_withdraw_locked(group_id)) or get_global_withdraw_lock(): return "🚫 Withdrawals are currently locked. Please contact admin."

return None

Usage in your message processing pipeline:

response = handle_admin_commands(phone, message, send_message, is_group, group_id)

if response is not None:

return

lock_message = check_lock_status(phone, group_id)

if lock_message:

send_message(phone, lock_message)

return

from pymongo import MongoClient import os import openai

from utils.shorten import shorten_link from utils.permissions import is_admin from utils.logging import log_activity from savecontacts import get_display_name

MongoDB setup

MONGO_URI = os.getenv("MONGO_URI") client = MongoClient(MONGO_URI) db = client.strangemindDB

vault_locks_collection = db.vault_locks withdraw_locks_collection = db.withdraw_locks users_collection = db.users  # Assuming for stats groups_collection = db.groups  # Assuming for stats

Lock/unlock functions

def lock_vault(target: str): vault_locks_collection.update_one( {"target": target}, {"$set": {"locked": True}}, upsert=True )

def unlock_vault(target: str): vault_locks_collection.update_one( {"target": target}, {"$set": {"locked": False}}, upsert=True )

def is_vault_locked(target: str) -> bool: lock = vault_locks_collection.find_one({"target": target}) return lock and lock.get("locked", False)

def lock_withdraw(target: str): withdraw_locks_collection.update_one( {"target": target}, {"$set": {"locked": True}}, upsert=True )

def unlock_withdraw(target: str): withdraw_locks_collection.update_one( {"target": target}, {"$set": {"locked": False}}, upsert=True )

def is_withdraw_locked(target: str) -> bool: lock = withdraw_locks_collection.find_one({"target": target}) return lock and lock.get("locked", False)

Admin command handler

def handle_admin_commands(phone, message): if not is_admin(phone): return None

msg_lower = message.lower().strip()

if msg_lower.startswith("lock vault "): target = msg_lower.split("lock vault ", 1)[1].strip() lock_vault(target) return f"Vault locked for '{target}'."

if msg_lower.startswith("unlock vault "): target = msg_lower.split("unlock vault ", 1)[1].strip() unlock_vault(target) return f"Vault unlocked for '{target}'."

if msg_lower.startswith("lock withdraw "): target = msg_lower.split("lock withdraw ", 1)[1].strip() lock_withdraw(target) return f"Withdrawals locked for '{target}'."

if msg_lower.startswith("unlock withdraw "): target = msg_lower.split("unlock withdraw ", 1)[1].strip() unlock_withdraw(target) return f"Withdrawals unlocked for '{target}'."

if msg_lower == "stats": total_users = users_collection.count_documents({}) total_groups = groups_collection.count_documents({}) return f"📊 Total users: {total_users}\n📊 Total groups: {total_groups}"

return None

OpenAI handler for admin

openai.api_key = os.getenv("OPENAI_API_KEY")

def handle_admin_openai(phone, message, send_message): if not is_admin(phone): return

msg = message.lower()

if msg.startswith("suggest:") or msg.startswith("issue:"): log_activity(phone, "user_feedback", message) send_message(phone, "✅ Your feedback has been logged and will be reviewed. Thanks!") return

try: response = openai.ChatCompletion.create( model="gpt-4", messages=[ {"role": "system", "content": "You are Strangemind AI's admin assistant. Reply concisely and practically."}, {"role": "user", "content": message} ] ) reply = response["choices"][0]["message"]["content"] send_message(phone, reply) log_activity(phone, "openai_response", message) except Exception as e: send_message(phone, "❌ OpenAI error: " + str(e))

Message router

def on_message_received(phone, message, send_message, is_group=False, group_id=None): # Admin check if is_admin(phone): handle_admin_openai(phone, message, send_message)

admin_response = handle_admin_commands(phone, message) if admin_response: send_message(phone, admin_response) return

Lock enforcement

target_id = group_id if is_group else phone if is_vault_locked(target_id): send_message(phone, "🚫 Vault access is locked currently. Contact admin.") return

if is_withdraw_locked(target_id): send_message(phone, "🚫 Withdrawals are locked currently. Contact admin.") return

AI response trigger

if "@strangemind ai" in message.lower(): if is_premium_user(group_id): stripped_query = message.lower().replace("@strangemind ai", "").strip() if stripped_query: ai_reply = get_openai_reply(stripped_query) send_message(group_id, ai_reply) else: send_message(group_id, "👋 I'm here! Ask me something like:\n@strangemind ai who invented Bitcoin?")
