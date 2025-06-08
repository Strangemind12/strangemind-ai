from savecontacts import get_display_name
from utils import is_premium_user

DEFAULT_INTRO_MESSAGE = "👋 Hi! I'm Strangemind AI. Mention me to get started."

def handle_auto_reply(phone, message, is_group, group_id=None):
    if is_group:
        # Group auto reply only if premium
        if is_premium_user(group_id):
            custom_name = get_display_name(phone)
            # You can customize the welcome message for groups
            return f"👋 Welcome {custom_name}! I'm {DEFAULT_INTRO_MESSAGE}"
        else:
            return None
    else:
        # Individual auto reply with optional intro message toggle
        if is_premium_user(phone):
            # In real case, fetch user settings for intro on/off; default on here
            return f"{DEFAULT_INTRO_MESSAGE}"
        else:
            return None
