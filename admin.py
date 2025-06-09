import os
import openai
from utils.shorten import shorten_link
from utils.permissions import is_admin
from utils.logging import log_activity
from savecontacts import get_display_name

# Load OpenAI API key from environment
openai.api_key = os.getenv("OPENAI_API_KEY")

def handle_admin_openai(phone, message, send_message):
    """
    Handles messages from WhatsApp admin users only.

    Supported:
    - Feedback: 'suggest:' or 'issue:'
    - Commands: 'cmd:ban <user>', 'cmd:broadcast <message>'
    - AI Chat: Any other message falls back to GPT-4
    """
    if not is_admin(phone):
        return  # Unauthorized access? We ghost.

    message_lower = message.lower()

    # ─── 1. Feedback Logging ─────────────────────────────
    if message_lower.startswith("suggest:") or message_lower.startswith("issue:"):
        log_activity(phone, "user_feedback", message)
        send_message(phone, "✅ Feedback received, boss. We’ll refine the system accordingly.")
        return

    # ─── 2. Command Handling (cmd:...) ───────────────────
    if message_lower.startswith("cmd:"):
        try:
            command = message[4:].strip()

            if command.startswith("ban "):
                target = command[4:].strip()
                # TODO: Hook this into your real ban logic
                log_activity(phone, "admin_command", f"ban {target}")
                send_message(phone, f"🚫 User {target} has been *flagged* for ban. (Demo only)")
                return

            elif command.startswith("broadcast "):
                msg = command[10:].strip()
                # TODO: Hook into real broadcast logic
                log_activity(phone, "admin_command", f"broadcast: {msg}")
                send_message(phone, f"📢 Broadcast queued: {msg}")
                return

            else:
                send_message(phone, "⚠️ Unknown admin command. Try again or type `cmd:help`.")
        except Exception as e:
            send_message(phone, f"❌ Command error: {str(e)}")
        return

    # ─── 3. GPT-4 Admin Assistant ───────────────────────
    try:
        response = openai.ChatCompletion.create(
            model="gpt-4",
            messages=[
                {
                    "role": "system",
                    "content": (
                        "You are Strangemind AI's personal assistant, replying only to admin commands. "
                        "Always be brief, strategic, and no-nonsense. Use clean formatting. Never repeat yourself."
                    )
                },
                {"role": "user", "content": message}
            ]
        )
        reply = response["choices"][0]["message"]["content"]
        send_message(phone, reply)
        log_activity(phone, "openai_response", message)

    except Exception as e:
        send_message(phone, f"❌ OpenAI error: {str(e)}")

# ─────────────────────────────────────────────────────
# ✅ USAGE EXAMPLE:
#
# Inside your WhatsApp message router:
#
#     if is_admin(phone):
#         handle_admin_openai(phone, message, send_message)
#         return
#
# This grants admins god-tier AI access with feedback + command power.
# ─────────────────────────────────────────────────────
