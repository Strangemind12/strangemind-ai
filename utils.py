from config import ENABLE_PREMIUM

# Dummy premium users/groups store — replace with real DB or cache in prod
premium_users = set([
    # example premium phone numbers or group IDs
    "+2348012345678",
    "group_1234567890",
])

def is_premium_user(identifier):
    if not ENABLE_PREMIUM:
        return False
    return identifier in premium_users


def send_message(recipient, message):
    # Here you'd call Gupshup API or WhatsApp API to send message
    # For now, just print for demo
    print(f"Sending message to {recipient}: {message}")
