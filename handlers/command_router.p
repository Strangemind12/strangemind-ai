# handlers/command_router.py

from handlers.admin_commands import handle_admin_command
from handlers.movie_handler import handle_movie_command
from utils.sender import send_message
from utils.admin_notify import notify_admin  # If you use admin alerts

def route_message(phone, message, is_group, group_id, is_admin=False):
    message = message.strip()

    if message.lower().startswith("/movie"):
        query = message[len("/movie"):].strip()
        if not query:
            send_message(phone, "❓ Please provide a movie name after the /movie command.")
        else:
            handle_movie_command(phone, query)
        return

    if is_admin:
        if handle_admin_command(phone, message, is_group, group_id):
            return

    if message.lower() == "/admin":
        send_message(phone, "👤 A human will reach out to you shortly. Hang tight!")
        notify_admin(phone, f"📨 New user escalation request from: {phone}")
        return

    if message.lower() == "/privacy":
        send_message(
            phone,
            "🔐 *Strangemind AI Privacy Policy*\nRead here: https://docs.google.com/document/d/YOUR_DOC_ID_HERE/view"
        )
        return

    if message.lower() == "/help":
        send_message(
            phone,
            """📘 *Strangemind AI Help Menu*

Type @strangemind ai followed by your question.

Commands:
• `/movie <title>` - Search for a movie
• `/admin` - Contact human support
• `/privacy` - View privacy policy
• `/help` - Show this menu

⚠️ I don’t store personal messages. I'm here to help, not to snoop. 🔐"""
        )
        return

    send_message(phone, "🤖 I'm not sure what that means. Type /help for a list of commands.")
