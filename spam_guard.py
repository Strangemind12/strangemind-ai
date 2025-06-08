from datetime import datetime, timedelta
from collections import defaultdict
from pymongo import MongoClient
from config import MONGO_URI, ADMIN_PHONE

# --- MongoDB Setup ---
client = MongoClient(MONGO_URI)
db = client.strangemindDB
vault_collection = db.vault

# --- Spam Detection Setup ---
message_history = defaultdict(list)
blacklist_words = [
    "scam", "fraud", "nude", "curseword1", "curseword2",
    "buy now", "free money", "click here", "subscribe", "cheap", "offer"
]
rate_limit_count = 5
rate_limit_seconds = 10

# --- Spam Detection Functions ---

def is_spammy(message: str) -> bool:
    msg = message.lower()
    return any(word in msg for word in blacklist_words)

def is_rate_limited(phone: str) -> bool:
    now = datetime.utcnow()
    recent = [t for t in message_history[phone] if now - t < timedelta(seconds=rate_limit_seconds)]
    message_history[phone] = recent + [now]
    return len(recent) > rate_limit_count

def detect_abuse(phone: str, message: str) -> str | None:
    if is_spammy(message):
        return "🚫 Inappropriate or spammy language detected. Please follow the rules."
    if is_rate_limited(phone):
        return "🕒 You're messaging too fast. Please wait a moment."
    return None

# --- Vault/Admin Functions ---

def shorten_link(url: str) -> str:
    # Dummy shortener for now, replace with real shortener service integration
    return f"http://short.link/{url[-6:]}"

def youtube_search(query: str):
    # Dummy YouTube search - return mock trailers
    return [{"url": f"https://youtube.com/watch?v=dQw4w9WgXcQ&search={query}"}]

def is_admin(phone: str) -> bool:
    return phone == ADMIN_PHONE

def get_vault_balance() -> float:
    vault = vault_collection.find_one({"admin": ADMIN_PHONE})
    if vault:
        return vault.get("balance", 0)
    return 0

def withdraw_from_vault(amount: float) -> bool:
    vault = vault_collection.find_one({"admin": ADMIN_PHONE})
    if vault and vault.get("balance", 0) >= amount:
        vault_collection.update_one({"admin": ADMIN_PHONE}, {"$inc": {"balance": -amount}})
        return True
    return False
