from datetime import datetime, timedelta
from pymongo import MongoClient
from flask import Flask, request, jsonify
import os

# --- DB Setup ---
MONGO_URI = os.getenv("MONGO_URI", "mongodb://localhost:27017/")
client = MongoClient(MONGO_URI)
db = client.strangemindDB  # unified DB name

# Collections (choose one or both based on your system)
premium_users_col = db.premium_users      # dedicated premium collection
users_col = db.contacts                    # main users collection

app = Flask(__name__)

# --- Premium Logic Using Dedicated Collection ---

def grant_premium(user_id: str, plan_type="monthly", payment_ref="manual_transfer") -> datetime:
    """
    Grant premium status using dedicated premium_users collection.
    """
    now = datetime.utcnow()
    duration = timedelta(days=30 if plan_type == "monthly" else 365)
    expiry = now + duration
    premium_users_col.update_one(
        {"user_id": user_id},
        {
            "$set": {
                "premium": True,
                "plan_type": plan_type,
                "payment_ref": payment_ref,
                "subscribed_at": now,
                "expires_at": expiry,
                "last_payment": now
            }
        },
        upsert=True
    )
    return expiry

def revoke_premium(user_id: str) -> bool:
    """
    Revoke premium status in dedicated collection.
    """
    premium_users_col.update_one({"user_id": user_id}, {"$set": {"premium": False}})
    return True

def is_premium(user_id: str) -> bool:
    """
    Check premium status in dedicated collection.
    Auto-revokes if expired.
    """
    user = premium_users_col.find_one({"user_id": user_id})
    if not user or not user.get("premium"):
        return False
    if user.get("expires_at") and user["expires_at"] < datetime.utcnow():
        revoke_premium(user_id)
        return False
    return True

def time_remaining(user_id: str) -> timedelta:
    """
    Returns remaining premium time or zero timedelta.
    """
    user = premium_users_col.find_one({"user_id": user_id})
    if user and user.get("expires_at"):
        remaining = user["expires_at"] - datetime.utcnow()
        return remaining if remaining.total_seconds() > 0 else timedelta(0)
    return timedelta(0)

# --- Premium Logic Using Users Collection (contacts) ---

def create_premium_user(phone: str, plan_type: str = "monthly", payment_ref: str = None) -> datetime:
    """
    Grant premium by updating the main users collection.
    """
    days = 30 if plan_type == "monthly" else 365
    expiry_date = datetime.utcnow() + timedelta(days=days)
    users_col.update_one(
        {"phone": phone},
        {
            "$set": {
                "is_premium": True,
                "premium_expiry": expiry_date,
                "plan_type": plan_type,
                "payment_ref": payment_ref,
                "subscribed_at": datetime.utcnow()
            }
        },
        upsert=True
    )
    return expiry_date

def is_premium_user(phone: str) -> bool:
    """
    Check premium status in users collection.
    """
    user = users_col.find_one({"phone": phone})
    if not user:
        return False
    expiry = user.get("premium_expiry")
    if expiry and expiry > datetime.utcnow():
        return True
    # Auto-revoke expired premium flag
    if user.get("is_premium"):
        users_col.update_one({"phone": phone}, {"$set": {"is_premium": False, "premium_expiry": None}})
    return False

def revoke_premium_user(phone: str) -> bool:
    """
    Revoke premium in users collection.
    """
    users_col.update_one({"phone": phone}, {"$set": {"is_premium": False, "premium_expiry": None}})
    return True

def time_remaining_user(phone: str) -> timedelta:
    """
    Remaining premium time from users collection.
    """
    user = users_col.find_one({"phone": phone})
    if user and user.get("premium_expiry"):
        remaining = user["premium_expiry"] - datetime.utcnow()
        return remaining if remaining.total_seconds() > 0 else timedelta(0)
    return timedelta(0)

# --- Decorator for Premium-only Features ---

def require_premium(func):
    def wrapper(user_id_or_phone, *args, **kwargs):
        # Check both collections for flexibility
        if not (is_premium(user_id_or_phone) or is_premium_user(user_id_or_phone)):
            return "⚠️ This feature is premium-only. Upgrade to access."
        return func(user_id_or_phone, *args, **kwargs)
    return wrapper

@require_premium
def access_premium_feature(user_id_or_phone):
    return "🎉 Welcome to premium feature X!"

# --- Flask API Route for Payment Webhook ---

@app.route('/api/payment-webhook', methods=['POST'])
def payment_webhook():
    data = request.json
    user_id = data.get("user_id") or data.get("phone")
    ref = data.get("reference")
    amount = float(data.get("amount", 0))
    plan = "monthly" if amount < 10000 else "yearly"

    if user_id and ref and amount > 0:
        # Here decide which method to use for granting premium
        # Example: prefer users collection for phone numbers
        expiry = create_premium_user(user_id, plan_type=plan, payment_ref=ref)
        # Or use: grant_premium(user_id, plan_type=plan, payment_ref=ref)
        return jsonify({"status": "success", "expires_at": expiry.isoformat()}), 200
    else:
        return jsonify({"status": "fail", "reason": "missing or invalid data"}), 400

if __name__ == "__main__":
    app.run(debug=True)
