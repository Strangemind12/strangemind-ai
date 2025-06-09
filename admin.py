Final merged and optimized admin and user command handler

import os import time import requests from datetime import datetime from pymongo import MongoClient from config import MONGO_URI, ADMIN_PHONE from whatsapp import send_message from utils.vault import get_vault_balance from utils.premium import toggle_premium_user, is_premium_user from utils.save import force_autosave, toggle_autosave

client = MongoClient(MONGO_URI) db = client.strangemindDB users_collection = db.users group_collection = db.groups ads_collection = db.ads messages_collection = db.messages errors_collection = db.errors

START_TIME = time.time()

=== Utilities ===

def is_admin(phone): return phone == ADMIN_PHONE

def shorten_link(url): api_key = os.getenv("SHRINKEARN_API_KEY") if not api_key: return url try: res = requests.get(f"https://shrinkearn.com/api?api={api_key}&url={url}") return res.json().get("shortenedUrl", url) except Exception as e: print("Shortener error:", e) return url

def shorten_links_in_message(text): words = text.split() return " ".join([shorten_link(w) if w.startswith("http") else w for w in words])

=== Lock / Admin Management ===

def lock_user(phone): users_collection.update_one({"phone": phone}, {"$set": {"locked": True}})

def unlock_user(phone): users_collection.update_one({"phone": phone}, {"$set": {"locked": False}})

def lock_group(group_id): group_collection.update_one({"group_id": group_id}, {"$set": {"locked": True}})

def unlock_group(group_id): group_collection.update_one({"group_id": group_id}, {"$set": {"locked": False}})

=== Stats ===

def total_users(): return users_collection.count_documents({})

def total_groups(): return group_collection.count_documents({})

def get_active_users(): return users_collection.count_documents({"locked": {"$ne": True}})

def get_locked_users(): return users_collection.count_documents({"locked": True})

def get_click_stats(): total_clicks = messages_collection.aggregate([ {"$match": {"shortened": True}}, {"$group": {"_id": None, "total": {"$sum": 1}}} ]) result = list(total_clicks) return result[0]['total'] if result else 0

=== Logging ===

def log_error(phone, error): errors_collection.insert_one({ "phone": phone, "error": str(error), "timestamp": datetime.utcnow() })

def get_recent_errors(limit=10): return list(errors_collection.find().sort("timestamp", -1).limit(limit))

=== Uptime ===

def get_uptime(): uptime_seconds = time.time() - START_TIME hours, remainder = divmod(int(uptime_seconds), 3600) minutes, seconds = divmod(remainder, 60) return f"🕒 Uptime: {hours}h {minutes}m {seconds}s"

=== Replies ===

def prepare_user_reply(text): return shorten_links_in_message(text)

def send_admin_announcement(phone, message): full_message = ( "📣 Admin Broadcast from Strangemind AI HQ 📣\n\n" f"🔔 Message:\n{message}\n\n" "Reply or tag @strangemind AI if you need support.\n" "– Team Strangemind" ) send_message(phone, full_message)

=== Admin Commands ===

def process_admin_command(phone, message): if not is_admin(phone): return "⛔ You are not authorized."

parts = message.strip().split()
cmd = parts[0].lower()

if cmd == "/lock" and len(parts) > 2 and parts[1] == "user":
    lock_user(parts[2])
    return "🔒 User locked."

if cmd == "/unlock" and len(parts) > 2 and parts[1] == "user":
    unlock_user(parts[2])
    return "🔓 User unlocked."

if cmd == "/ban" and len(parts) == 2:
    users_collection.update_one({"phone": parts[1]}, {"$set": {"banned": True}})
    return f"🚫 User {parts[1]} banned."

if cmd == "/unban" and len(parts) == 2:
    users_collection.update_one({"phone": parts[1]}, {"$unset": {"banned": ""}})
    return f"✅ User {parts[1]} unbanned."

if cmd == "/premium" and len(parts) == 2:
    users_collection.update_one({"phone": parts[1]}, {"$set": {"is_premium": True}}, upsert=True)
    return f"🌟 User {parts[1]} upgraded to Premium."

if cmd == "/vault" and len(parts) == 2:
    bal = get_vault_balance(parts[1])
    return f"💰 Vault Balance for {parts[1]}: {bal} coins"

if cmd == "/userinfo" and len(parts) == 2:
    user = users_collection.find_one({"phone": parts[1]})
    if not user:
        return "❌ User not found."
    return (
        f"📇 User Info:\n"
        f"Name: {user.get('name')}\n"
        f"Phone: {user.get('phone')}\n"
        f"Premium: {user.get('is_premium')}\n"
        f"Joined: {user.get('joined')}"
    )

if cmd == "/broadcast":
    msg = message.replace("/broadcast", "").strip()
    if not msg:
        return "⚠️ Message is empty."
    final_msg = shorten_links_in_message(msg)
    users = users_collection.find({})
    for user in users:
        send_admin_announcement(user.get("phone"), final_msg)
    return f"📢 Broadcast sent to {users_collection.count_documents({})} users."

if cmd == "/stats":
    return f"👥 Users: {total_users()} | 👪 Groups: {total_groups()} | 🔓 Active: {get_active_users()} | 🔒 Locked: {get_locked_users()}"

if cmd == "/save":
    force_autosave()
    return "💾 Manual save triggered."

if cmd == "/autosave":
    toggle_autosave(phone)
    return "🔄 Toggled auto-save setting."

if cmd == "/errors":
    errors = get_recent_errors()
    return "\n".join([f"{e['timestamp']} - {e['error']}" for e in errors]) or "📭 No recent errors."

if cmd == "/uptime":
    return get_uptime()

if cmd == "/earnings":
    return "💸 Earnings: Coming Soon | Under Upgrade 💻"

return "🧭 Command received, but unrecognized. Please check syntax."

=== Exported functions ===

def handle_admin_or_reply(phone, message): """Main entry point for admin command or system replies with link shortening.""" if is_admin(phone): result = process_admin_command(phone, message) if result: send_message(phone, result) return True return False

