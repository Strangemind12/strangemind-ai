from datetime import datetime, timedelta
from pymongo import MongoClient
from config import MONGO_URI, ADMIN_PHONE, NIGERIA_MONTHLY_PRICE, ENABLE_PREMIUM

# Connect to MongoDB
client = MongoClient(MONGO_URI)
db = client.strangemindDB
users_collection = db.contacts
vault_collection = db.vault

# ✅ Check if user is admin
def is_admin(phone: str) -> bool:
    return phone == ADMIN_PHONE

# ✅ Send a message (replace with real WhatsApp/Gupshup API call)
def send_message(to_phone: str, message: str):
    print(f"[Sending to {to_phone}]: {message}")  # Stub for API integration

# ✅ Grant premium with expiry and vault update
def grant_premium(phone: str, days: int = 30):
    expiry_date = datetime.utcnow() + timedelta(days=days)
    users_collection.update_one(
        {"phone": phone},
        {"$set": {"is_premium": True, "premium_expiry": expiry_date}},
        upsert=True
    )
    vault_collection.update_one(
        {"admin": ADMIN_PHONE},
        {"$inc": {"balance": NIGERIA_MONTHLY_PRICE}},
        upsert=True
    )
    return expiry_date

# ✅ Revoke premium
def revoke_premium(phone: str):
    users_collection.update_one(
        {"phone": phone},
        {"$set": {"is_premium": False, "premium_expiry": None}}
    )

# ✅ Check if a user is premium and not expired
def check_premium(phone: str) -> bool:
    if not ENABLE_PREMIUM:
        return False

    user = users_collection.find_one({"phone": phone})
    if not user:
        return False

    expiry = user.get("premium_expiry")
    if expiry and expiry > datetime.utcnow():
        return True

    # Auto-revoke if expired
    if user.get("is_premium", False):
        revoke_premium(phone)

    return False

# ✅ Premium check shortcut for use in webhook
def is_premium_user(identifier: str) -> bool:
    return check_premium(identifier)

# ✅ Vault balance checker (admin only)
def get_vault_balance():
    vault = vault_collection.find_one({"admin": ADMIN_PHONE})
    return vault.get("balance", 0.0) if vault else 0.0

# ✅ Vault withdraw (admin only)
def withdraw_from_vault(amount: float) -> bool:
    vault = vault_collection.find_one({"admin": ADMIN_PHONE})
    if not vault or vault.get("balance", 0.0) < amount:
        return False

    vault_collection.update_one(
        {"admin": ADMIN_PHONE},
        {"$inc": {"balance": -amount}}
    )
    return True
