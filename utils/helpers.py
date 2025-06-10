import os
import requests
from pymongo import MongoClient

# --- Mongo Setup ---
client = MongoClient(os.getenv("MONGO_URI"))
db = client.strangemindDB

autosave_col = db.autosave_settings  # Vault/earnings removed

# --- Short.io Monetization ---
def monetize_link(url):
    api_key = os.getenv("SHORTIO_API_KEY")  # Example: "your-shortio-api-key"
    domain = os.getenv("SHORTIO_DOMAIN")    # Example: "strangemind.link"
    
    headers = {
        "Content-Type": "application/json",
        "Authorization": api_key
    }
    payload = {
        "domain": domain,
        "originalURL": url
    }
    
    try:
        res = requests.post("https://api.short.io/links", json=payload, headers=headers)
        data = res.json()
        return data.get("shortURL", url)
    except Exception as e:
        print(f"[Short.io Error] {e}")
        return url

# --- Message Sender (stub for Meta WhatsApp API) ---
def send_message(phone, text):
    print(f"[SEND] To {phone}: {text}")  # Hook to actual WhatsApp API later

# --- Autosave Settings ---
def is_autosave_enabled(user_or_group):
    rec = autosave_col.find_one({"user": user_or_group})
    return bool(rec and rec.get("enabled", False))

def set_autosave(user_or_group, status: bool):
    autosave_col.update_one({"user": user_or_group}, {"$set": {"enabled": status}}, upsert=True)

# --- Admin Checker ---
def is_admin(phone):
    return phone == os.getenv("ADMIN_PHONE")
