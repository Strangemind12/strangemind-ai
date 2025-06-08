from savecontacts import get_display_name
from utils import is_premium_user
from flask import jsonify

DEFAULT_INTRO_MESSAGE = "👋 Hi! I'm Strangemind AI. Mention me to get started."

def handle_auto_reply(phone, message, is_group, group_id=None):
    lower_msg = message.lower().strip()

    # Check if someone tagged @strangemind ai directly
    if "@strangemind ai" in lower_msg:
        if lower_msg == "@strangemind ai":
            # For group mentions
            if is_group and is_premium_user(group_id):
                return """📦 *Welcome to Strangemind AI* 📦

Here's what I can do 👇

🧠 *Smart Stuff* (Powered by OpenAI)  
→ Just tag and ask: `@strangemind who is Mandela?`

🎬 *Movies*  
→ `/search movie name` - trailer + download links

🌐 *Google Downloads*  
→ Auto extract direct links (MediaFire, Mega, GDrive)

💸 *Earn from Clicks*  
→ Link shortener = vault earnings

Type any command or ask a question!"""

            # For individual mentions (only for premium users)
            elif not is_group and is_premium_user(phone):
                return """📦 *Welcome to Strangemind AI* 📦

Here's what I can do 👇

🧠 *Smart Stuff* (Powered by OpenAI)  
→ Just tag and ask: `@strangemind who is Mandela?`

🎬 *Movies*  
→ `/search movie name` - trailer + download links

🌐 *Google Downloads*  
→ Auto extract direct links (MediaFire, Mega, GDrive)

💸 *Earn from Clicks*  
→ Link shortener = vault earnings

Type any command or ask a question!"""

            # Not premium – ignore
            else:
                return None

    # Normal group welcome response
    if is_group:
        if is_premium_user(group_id):
            custom_name = get_display_name(phone)
            return f"👋 Welcome {custom_name}! I'm {DEFAULT_INTRO_MESSAGE}"
        else:
            return None
    else:
        if is_premium_user(phone):
            return f"{DEFAULT_INTRO_MESSAGE}"
        else:
            return None
