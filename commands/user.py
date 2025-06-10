from helpers.database import save_user_info
from helpers.messaging import send_message
from helpers.consent import has_consented, set_consent

def handle_user_command(phone, message, is_group, group_id):
    message = message.lower()

    if message == "/start":
        if not has_consented(phone):
            send_message(phone, "🧠 Welcome! To activate me and enable full features in groups, reply with /consent.")
        else:
            send_message(phone, "✅ You're already activated. Type /help to explore my commands.")

    elif message == "/consent":
        set_consent(phone, True)
        save_user_info(phone)
        send_message(phone, "🎉 Consent saved! I’ll now assist you even in groups with smarter replies.")

    # ... other commands ...
