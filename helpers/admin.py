from helpers.messaging import send_message

ADMIN_PHONE_NUMBERS = ["2348100000000", "2347012345678"]  # Replace with real admin numbers

def notify_admin(user_phone, message):
    for admin in ADMIN_PHONE_NUMBERS:
        send_message(admin, f"🚨 Escalation: User {user_phone} needs human help.\nMessage: {message}")
