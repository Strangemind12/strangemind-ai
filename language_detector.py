# strangemind_ai/premium_user_model.py

from datetime import datetime, timedelta
from pymongo import MongoClient
import os

# --- LANGUAGE DETECTION ---
try:
    from langdetect import detect
except ImportError:
    raise ImportError("Please run 'pip install langdetect' to enable language detection.")

def detect_language(text):
    try:
        return detect(text)
    except:
        return "en"  # fallback to English if detection fails

# --- TRANSLATIONS / LOCALES ---
translations = {
    "en": {
        "premium_required": "⚠️ This feature is premium-only. Upgrade to access.",
        "welcome_premium": "🎉 Welcome to premium feature X!"
    },
    "fr": {
        "premium_required": "⚠️ Cette fonctionnalité est réservée aux membres premium. Passez à la version supérieure.",
        "welcome_premium": "🎉 Bienvenue dans la fonctionnalité premium X !"
    },
    "es": {
        "premium_required": "⚠️ Esta función es solo para usuarios premium. Actualízate para acceder.",
        "welcome_premium": "🎉 ¡Bienvenido a la función premium X!"
    },
    "yo": {
        "premium_required": "⚠️ Ẹ̀ka yìí fún àwọn oníbàárà premium péré ni. Ṣe ìmúdájú.",
        "welcome_premium": "🎉 Kaabọ sí iṣẹ́ premium X!"
    },
}

def translate(message_key, lang_code="en"):
    if lang_code in translations and message_key in translations[lang_code]:
        return translations[lang_code][message_key]
    return translations["en"].get(message_key, message_key)  # fallback to English

# --- MONGO SETUP ---
MONGO_URI = os.getenv("MONGO_URI", "mongodb://localhost:27017/")
client = MongoClient(MONGO_URI)
db = client["strangemind"]
premium_users = db["premium_users"]

# --- PREMIUM USER MANAGEMENT ---

def create_premium_user(phone, plan_type="monthly", payment_ref=None):
    now = datetime.utcnow()
    expiry = now + timedelta(days=30 if plan_type == "monthly" else 365)

    premium_users.update_one(
        {"phone": phone},
        {"$set": {
            "premium": True,
            "plan_type": plan_type,
            "subscription_start": now,
            "subscription_expiry": expiry,
            "payment_ref": payment_ref,
            "last_payment": now
        }},
        upsert=True
    )
    return True

def is_premium(phone):
    user = premium_users.find_one({"phone": phone})
    if not user or not user.get("premium"):
        return False
    if user["subscription_expiry"] < datetime.utcnow():
        premium_users.update_one({"phone": phone}, {"$set": {"premium": False}})
        return False
    return True

def time_remaining(phone):
    user = premium_users.find_one({"phone": phone})
    return user["subscription_expiry"] - datetime.utcnow() if user and user.get("subscription_expiry") else timedelta(0)

def grant_premium(phone, days):
    now = datetime.utcnow()
    expiry = now + timedelta(days=days)
    premium_users.update_one(
        {"phone": phone},
        {"$set": {
            "premium": True,
            "subscription_start": now,
            "subscription_expiry": expiry,
            "payment_ref": "admin-granted",
            "last_payment": now
        }},
        upsert=True
    )
    return True

def revoke_premium(phone):
    premium_users.update_one({"phone": phone}, {"$set": {"premium": False}})
    return True

# --- DECORATOR WITH LANGUAGE SUPPORT ---

def require_premium(func):
    def wrapper(phone, message_text, *args, **kwargs):
        lang = detect_language(message_text)
        if not is_premium(phone):
            return translate("premium_required", lang)
        return func(phone, lang, *args, **kwargs)
    return wrapper

@require_premium
def access_premium_feature(phone, lang):
    return translate("welcome_premium", lang)

# --- TEST STUB ---
if __name__ == "__main__":
    test_phone = "+1234567890"
    test_msg = "Bonjour, je veux accéder à la fonctionnalité premium."
    
    # Create user premium status
    create_premium_user(test_phone, plan_type="monthly", payment_ref="test-ref-001")
    
    # Test premium access
    print(access_premium_feature(test_phone, test_msg))  # Should print French welcome msg
    
    # Test revoke
    revoke_premium(test_phone)
    print(access_premium_feature(test_phone, test_msg))  # Should print French premium_required msg
