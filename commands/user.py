from helpers.consent import has_consented, set_consent

def handle_user_command(phone, message, is_group, group_id):
    message_lower = message.lower()

    if "/start" in message_lower:
        set_consent(phone)
        send_message(phone, "✅ You're now connected to Strangemind AI. Type /help to begin.")
        return

    if not has_consented(phone):
        send_message(phone, "👋 Please type /start in private chat to activate Strangemind AI.")
        return
