# admin/commands.py

from utils import is_admin, is_premium_user, get_vault_balance, withdraw_from_vault
from database import users_collection, vault_collection, history_collection
from datetime import datetime
import time
import os
import platform
import psutil

# System uptime tracker
START_TIME = time.time()

# In-memory admin settings (replace with DB later)
admin_settings = {
    "autosave": True,
    "abuse_log": []
}

def send_admin_announcement(phone: str, message: str):
    """
    Sends an announcement from the admin to a user via WhatsApp API.
    """
    full_message = (
        "📣 *Admin Broadcast from Strangemind AI HQ* 📣\n\n"
        f"🔔 Message from Command:\n"
        f"_{message}_\n\n"
        "If you have questions or feedback, just reply or tag @strangemind AI.\n\n"
        "🚀 Stay sharp. Stay curious.\n"
        "– Team Strangemind"
    )
    send_message(phone, full_message)


def get_uptime():
    uptime_seconds = time.time() - START_TIME
    hours, remainder = divmod(int(uptime_seconds), 3600)
    minutes, seconds = divmod(remainder, 60)
    return f"🕒 Uptime: {hours}h {minutes}m {seconds}s"


def handle_admin_command(phone, command):
    if not is_admin(phone):
        return "⛔ You are not authorized to use admin commands."

    parts = command.strip().split()
    cmd = parts[0].lower()

    if cmd == "/autosave":
        admin_settings["autosave"] = not admin_settings["autosave"]
        return f"💾 Auto-save is now {'enabled' if admin_settings['autosave'] else 'disabled'}."

    elif cmd == "/status":
        return f"✅ Bot is active\n{get_uptime()}\nAuto-save: {'ON' if admin_settings['autosave'] else 'OFF'}"

    elif cmd == "/vault":
        if len(parts) < 2:
            return "❌ Usage: /vault <phone>"
        target = parts[1]
        balance = get_vault_balance(target)
        return f"💰 Vault for {target}: {balance} coins"

    elif cmd == "/userinfo":
        if len(parts) < 2:
            return "❌ Usage: /userinfo <phone>"
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

    elif cmd == "/premium":
        if len(parts) < 2:
            return "❌ Usage: /premium <phone>"
        users_collection.update_one({"phone": parts[1]}, {"$set": {"is_premium": True}}, upsert=True)
        return f"🌟 {parts[1]} is now a premium user."

    elif cmd == "/broadcast":
        msg = command.replace("/broadcast", "").strip()
        if not msg:
            return "❌ Message is empty."
        # Loop through all users and send the announcement
        users = users_collection.find({})
        for user in users:
            send_admin_announcement(user.get("phone"), msg)
        return f"📢 Broadcast sent to {users_collection.count_documents({})} users."

    elif cmd == "/ban":
        if len(parts) < 2:
            return "❌ Usage: /ban <phone>"
        users_collection.update_one({"phone": parts[1]}, {"$set": {"banned": True}})
        return f"🔒 User {parts[1]} has been banned."

    elif cmd == "/unban":
        if len(parts) < 2:
            return "❌ Usage: /unban <phone>"
        users_collection.update_one({"phone": parts[1]}, {"$unset": {"banned": ""}})
        return f"✅ User {parts[1]} is unbanned."

    elif cmd == "/abuse log":
        if not admin_settings["abuse_log"]:
            return "📭 No abuse reports yet."
        return "🚨 Abuse Reports:\n" + "\n".join(admin_settings["abuse_log"])

    elif cmd == "/groups":
        # You should keep track of groups in DB or memory
        return "👥 Active groups: [Wired from DB in production]"

    elif cmd == "/referral":
        if len(parts) < 2:
            return "❌ Usage: /referral <phone>"
        user = users_collection.find_one({"phone": parts[1]})
        return f"📣 Referred by: {user.get('referred_by', 'None')}"

    elif cmd == "/setname":
        if len(parts) < 3:
            return "❌ Usage: /setname <phone> <name>"
        users_collection.update_one({"phone": parts[1]}, {"$set": {"name": ' '.join(parts[2:])}})
        return f"✏️ Name updated for {parts[1]}"

    elif cmd == "/resetvault":
        if len(parts) < 2:
            return "❌ Usage: /resetvault <phone>"
        vault_collection.update_one({"user": parts[1]}, {"$set": {"balance": 0}}, upsert=True)
        return f"💸 Vault reset for {parts[1]}"

    elif cmd == "/uptime":
        return get_uptime()

    else:
        return f"❓ Unknown admin command: {cmd}"
