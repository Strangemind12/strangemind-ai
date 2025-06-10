from helpers.database import save_user_info  # ✅ Custom save logic
from helpers.messaging import send_message
from helpers.consent import has_consented, set_consent  # New consent module

def handle_user_command(phone, message, is_group, group_id):
    message = message.lower()

    if message == "/start":
        if not has_consented(phone):
            send_message(phone, "🧠 Hey! Want smarter replies from me? Reply with /consent to let me save your preferences.")
        else:
            send_message(phone, "✅ You’ve already activated Strangemind AI. Type /help to see commands.")
    
    elif message == "/consent":
        set_consent(phone, True)
        save_user_info(phone)  # Store phone to DB, Mongo, whatever
        send_message(phone, "🎉 You’re all set! I’ll remember your preferences for better replies.")
    
    # ... other commands ...
