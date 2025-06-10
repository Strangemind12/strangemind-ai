from handlers.movie_handler import handle_movie_command
from utils.messaging import send_message
from utils.admin_notify import notify_admin  # Assuming you have this somewhere

def handle_user_command(phone, message, is_group, group_id):
    message = message.strip()

    if message.lower().startswith("/movie"):
        query = message[6:].strip()
        if not query:
            send_message(phone, "⚠️ Please provide a movie name. Usage: `/movie Avengers Endgame`")
        else:
            handle_movie_command(phone, query)
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

Type `@strangemind ai` followed by your question.

Commands:
• `/admin` - Contact human support
• `/privacy` - View privacy policy
• `/help` - Show this menu

⚠️ I don’t store personal messages. I'm here to help, not to snoop. 🔐"""
        )
        return

    # Add other command handlers here...
