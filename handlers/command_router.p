def handle_user_command(phone, message, is_group, group_id):
    message = message.strip().lower()

    if message == "/admin":
        send_message(phone, "👤 A human will reach out to you shortly. Hang tight!")
        notify_admin(phone, f"📨 New user escalation request from: {phone}")
        return

    if message == "/privacy":
        send_message(
            phone,
            "🔐 *Strangemind AI Privacy Policy*\nRead here: https://docs.google.com/document/d/YOUR_DOC_ID_HERE/view"
        )
        return

    if message == "/help":
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
