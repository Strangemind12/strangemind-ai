import time from utils import ( is_admin, lock_user, unlock_user, lock_group, unlock_group, is_locked, is_premium, make_premium, remove_premium, shorten_url, save_data, set_autosave, get_stats, get_logs, broadcast_message, get_uptime, set_user_vault, get_user_vault, ban_user, unban_user, is_banned )

def handle_admin_commands(sender_id, message): if not is_admin(sender_id): return "🚫 You are not authorized to use admin commands."

command = message.lower()

if command.startswith("/lock user"):
    user_id = command.split("/lock user", 1)[1].strip()
    lock_user(user_id)
    return f"🔒 User {user_id} has been locked."

elif command.startswith("/unlock user"):
    user_id = command.split("/unlock user", 1)[1].strip()
    unlock_user(user_id)
    return f"🔓 User {user_id} has been unlocked."

elif command.startswith("/lock group"):
    group_id = command.split("/lock group", 1)[1].strip()
    lock_group(group_id)
    return f"🔒 Group {group_id} has been locked."

elif command.startswith("/unlock group"):
    group_id = command.split("/unlock group", 1)[1].strip()
    unlock_group(group_id)
    return f"🔓 Group {group_id} has been unlocked."

elif command.startswith("/ban"):
    user_id = command.split("/ban", 1)[1].strip()
    ban_user(user_id)
    return f"🚫 User {user_id} has been banned."

elif command.startswith("/unban"):
    user_id = command.split("/unban", 1)[1].strip()
    unban_user(user_id)
    return f"✅ User {user_id} has been unbanned."

elif command.startswith("/make premium"):
    user_id = command.split("/make premium", 1)[1].strip()
    make_premium(user_id)
    return f"👑 User {user_id} is now premium."

elif command.startswith("/remove premium"):
    user_id = command.split("/remove premium", 1)[1].strip()
    remove_premium(user_id)
    return f"💸 User {user_id} is no longer premium."

elif command.startswith("/set vault"):
    parts = command.split()
    if len(parts) == 4:
        _, _, user_id, amount = parts
        set_user_vault(user_id, float(amount))
        return f"💰 Vault set: {user_id} now has {amount} coins."
    else:
        return "❌ Usage: /set vault <user_id> <amount>"

elif command.startswith("/get vault"):
    user_id = command.split("/get vault", 1)[1].strip()
    vault = get_user_vault(user_id)
    return f"💼 {user_id} has {vault} coins."

elif command.startswith("/broadcast"):
    message_to_send = command.split("/broadcast", 1)[1].strip()
    shortened = shorten_url(message_to_send)
    broadcast_message(shortened)
    return "📢 Broadcast sent with short link."

elif command.startswith("/stats"):
    stats = get_stats()
    return f"📊 Bot Stats:\n{stats}"

elif command.startswith("/logs"):
    logs = get_logs()
    return f"🧾 Recent Logs:\n{logs}"

elif command.startswith("/save"):
    save_data()
    return "💾 Data saved manually."

elif command.startswith("/autosave"):
    setting = command.split("/autosave", 1)[1].strip()
    if setting in ["on", "off"]:
        set_autosave(setting == "on")
        return f"🔁 Autosave {'enabled' if setting == 'on' else 'disabled'}."
    else:
        return "❌ Use /autosave on OR /autosave off"

elif command.startswith("/uptime"):
    return f"⏱️ Uptime: {get_uptime()}"

else:
    return "❌ Unknown admin command."

def handle_user_commands(user_id, message): if is_locked(user_id): return "🔒 You are currently locked. Contact admin." if is_banned(user_id): return "⛔ You are banned. Appeal to support."

message = message.strip()
if message.startswith("/vault"):
    balance = get_user_vault(user_id)
    return f"💼 Your vault contains {balance} coins."

elif message.startswith("/premium"):
    if is_premium(user_id):
        return "👑 You are a premium user."
    else:
        return "💸 You are on the free plan. Upgrade for full features."

elif message.startswith("/help"):
    return "🤖 Available commands:\n/vault - Check balance\n/premium - Premium status\n/help - This menu"

return "❔ Unknown command. Type /help to see available options."

def route_command(sender_id, message): if message.startswith("/"): if is_admin(sender_id): return handle_admin_commands(sender_id, message) else: return handle_user_commands(sender_id, message) return None  # Non-command messages handled elsewhere

