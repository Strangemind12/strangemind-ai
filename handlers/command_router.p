import os
import openai
from pymongo import MongoClient

from utils.helpers import is_admin
from utils.logging import log_activity
from helpers.messaging import send_message
from helpers.admin import notify_admin
from ai_engine import get_openai_reply
from helpers.consent import has_consented

# --- Setup ---
MONGO_URI = os.getenv("MONGO_URI")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

client = MongoClient(MONGO_URI)
db = client.strangemindDB
users_collection = db.users
groups_collection = db.groups

openai.api_key = OPENAI_API_KEY

# --- Admin Commands ---
def handle_admin_commands(phone, message):
    if not is_admin(phone):
        return None

    msg = message.lower().strip()

    if msg == "stats":
        total_users = users_collection.count_documents({})
        total_groups = groups_collection.count_documents({})
        return f"📊 Total users: {total_users}\n📊 Total groups: {total_groups}"

    return None

def handle_admin_openai(phone, message):
    if not is_admin(phone):
        return

    if message.lower().startswith(("suggest:", "issue:")):
        log_activity(phone, "user_feedback", message)
        send_message(phone, "✅ Your feedback has been logged and will be reviewed. Thanks!")
        return

    try:
        response = openai.ChatCompletion.create(
            model="gpt-4",
            messages=[
                {"role": "system", "content": "You are Strangemind AI's admin assistant. Reply concisely and practically."},
                {"role": "user", "content": message}
            ]
        )
        reply = response["choices"][0]["message"]["content"]
        send_message(phone, reply)
        log_activity(phone, "openai_response", message)
    except Exception as e:
        send_message(phone, "❌ OpenAI error: " + str(e))

# --- User Commands ---
def handle_user_command(phone, message, is_group, group_id):
    message = message.strip().lower()

    if message == "/admin":
        send_message(phone, "👤 A human will reach out to you shortly. Hang tight!")
        notify_admin(phone, f"📨 New user escalation request from: {phone}")
        return

    if message == "/help":
        send_message(phone, "📘 *Strangemind AI Help Menu*\n\nType `@strangemind ai` followed by your question.\nCommands:\n• `/admin` - Contact human support\n• `/help` - Show this menu\n\n⚠️ I don’t store personal messages. I'm here to help, not to snoop. 🔐")
        return

# --- Main Router ---
def route_message(phone, message, is_group=False, group_id=None, is_admin=False):
    message_lower = message.lower().strip()

    # ✅ Check for consent in groups
    if is_group and not has_consented(phone):
        send_message(phone, "👋 Please DM me with /start to activate Strangemind AI.")
        return

    # ✅ Admin logic
    if is_admin or is_admin(phone):
        handle_admin_openai(phone, message)
        admin_response = handle_admin_commands(phone, message)
        if admin_response:
            send_message(phone, admin_response)
        return

    # ✅ Greeting triggers
    if message_lower in ["/start", "hi", "hello"]:
        send_message(phone, "👋 Hi! I'm *Strangemind AI*.\nType `@strangemind ai` followed by your question.\n⚠️ I don’t store personal messages.")
    
    # ✅ User commands
    handle_user_command(phone, message, is_group, group_id)

    # ✅ AI mention handler
    if "@strangemind ai" in message_lower:
        stripped_query = message_lower.replace("@strangemind ai", "").strip()
        if stripped_query:
            reply = get_openai_reply(stripped_query)
            send_message(group_id if is_group else phone, reply)
        else:
            send_message(group_id if is_group else phone, "👋 I'm here! Ask me something like:\n@strangemind ai who invented Bitcoin?")
