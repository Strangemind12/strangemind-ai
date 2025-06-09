import os
import openai
from utils.shorten import shorten_link
from utils.permissions import is_admin
from utils.logging import log_activity
from savecontacts import get_display_name

# External DB references (assume imported or injected)
from database import vault_collection, global_settings_collection

# Load OpenAI key
openai.api_key = os.getenv("OPENAI_API_KEY")


def handle_admin(phone, message, send_message, is_group=False, group_id=None):
    if not is_admin(phone):
        return  # 🕶️ Unauthorized

    msg = message.strip()
    msg_lower = msg.lower()
    tokens = msg_lower.split()

    if not tokens:
        send_message(phone, "⚠️ Empty admin command received.")
        return

    # ───── 1. Feedback Commands ─────────────────────────
    if msg_lower.startswith("suggest:") or msg_lower.startswith("issue:"):
        log_activity(phone, "user_feedback", msg)
        send_message(phone, "📝 Feedback logged. We'll refine accordingly.")
        return

    # ───── 2. CMD-Prefix Based Commands ─────────────────
    if msg_lower.startswith("cmd:"):
        handle_structured_admin_cmd(phone, msg[4:].strip(), send_message)
        return

    # ───── 3. Slash Commands (/lockvault etc) ───────────
    if tokens[0] in ["/lockvault", "/unlockvault"]:
        return handle_vault_control(phone, tokens, send_message, is_group, group_id)

    elif tokens[0] in ["/withdrawlock", "/withdrawunlock"]:
        return handle_global_withdrawal(phone, tokens[0], send_message, is_group, group_id)

    # ───── 4. GPT-4 AI Assistant Fallback ───────────────
    try:
        response = openai.ChatCompletion.create(
            model="gpt-4",
            messages=[
                {"role": "system", "content": (
                    "You are Strangemind AI’s assistant for admin users only. Be brief, intelligent, and strategic. "
                    "Never give long-winded explanations. Avoid repetition. Format cleanly."
                )},
                {"role": "user", "content": msg}
            ]
        )
        reply = response["choices"][0]["message"]["content"]
        send_message(phone, reply)
        log_activity(phone, "openai_response", msg)

    except Exception as e:
        send_message(phone, f"❌ OpenAI error: {str(e)}")


# ───── Helper: Structured cmd: Commands ────────────────
def handle_structured_admin_cmd(phone, command, send_message):
    try:
        if command.startswith("ban "):
            target = command[4:].strip()
            log_activity(phone, "admin_command", f"ban {target}")
            send_message(phone, f"🚫 User {target} flagged for ban (simulation).")
            return

        elif command.startswith("broadcast "):
            msg = command[10:].strip()
            log_activity(phone, "admin_command", f"broadcast: {msg}")
            send_message(phone, f"📢 Broadcast sent: {msg}")
            return

        else:
            send_message(phone, "⚠️ Unknown admin command. Use `cmd:help` for available ops.")

    except Exception as e:
        send_message(phone, f"❌ Command error: {str(e)}")


# ───── Helper: Lock/Unlock Vault ───────────────────────
def handle_vault_control(phone, tokens, send_message, is_group, group_id):
    if len(tokens) < 2 or not tokens[1].startswith("@"):
        send_message(phone, "⚠️ Usage: `/lockvault @user123` or `/unlockvault @group456`")
        return

    target_id = tokens[1][1:]  # strip '@'
    is_lock = tokens[0] == "/lockvault"

    vault_collection.update_one(
        {"user": target_id},
        {"$set": {"vault_locked": is_lock}},
        upsert=True
    )

    response = f"🔐 Vault has been {'🔒 locked' if is_lock else '🔓 unlocked'} for `{tokens[1]}`"
    send_message(group_id if is_group else phone, response)


# ───── Helper: Global Withdrawal Toggle ────────────────
def handle_global_withdrawal(phone, command, send_message, is_group, group_id):
    is_lock = command == "/withdrawlock"
    global_settings_collection.update_one(
        {"setting": "withdrawal_lock"},
        {"$set": {"value": is_lock}},
        upsert=True
    )
    status_text = (
        "🚫 Global withdrawal is *LOCKED*." if is_lock else "✅ Withdrawals are *UNLOCKED* globally."
    )
    send_message(group_id if is_group else phone, status_text)
