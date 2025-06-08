# strangemind_ai/premium_user_model.py

from datetime import datetime, timedelta
from pymongo import MongoClient
from flask import Flask, request, jsonify
import os

# --- DB Setup ---
MONGO_URI = os.getenv("MONGO_URI", "mongodb://localhost:27017/")
client = MongoClient(MONGO_URI)
db = client["strangemind"]
premium_users = db["premium_users"]

# --- Core Premium Logic ---

def grant_premium(user_id, plan_type="monthly", payment_ref="manual_transfer"):
    now = datetime.utcnow()
    duration = timedelta(days=30 if plan_type == "monthly" else 365)
    expiry = now + duration
    premium_users.update_one(
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

def revoke_premium(user_id):
    premium_users.update_one({"user_id": user_id}, {"$set": {"premium": False}})
    return True

def is_premium(user_id):
    user = premium_users.find_one({"user_id": user_id})
    if not user or not user.get("premium"):
        return False
    if user.get("expires_at") and user["expires_at"] < datetime.utcnow():
        premium_users.update_one({"user_id": user_id}, {"$set": {"premium": False}})
        return False
    return True

def time_remaining(user_id):
    user = premium_users.find_one({"user_id": user_id})
    if user and user.get("expires_at"):
        return user["expires_at"] - datetime.utcnow()
    return timedelta(0)

# --- Decorator for Premium-only Features ---

def require_premium(func):
    def wrapper(user_id, *args, **kwargs):
        if not is_premium(user_id):
            return "⚠️ This feature is premium-only. Upgrade to access."
        return func(user_id, *args, **kwargs)
    return wrapper

# Example Usage
@require_premium
def access_premium_feature(user_id):
    return "🎉 Welcome to premium feature X!"

# --- Webhook for Manual Payment Trigger (SMSGate-compatible) ---
# This is optional if using webhook-style confirmation.

app = Flask(__name__)

@app.route('/api/payment-webhook', methods=['POST'])
def payment_webhook():
    data = request.json
    user_id = data.get("user_id") or data.get("phone")  # fallback
    ref = data.get("reference")
    amount = int(data.get("amount", 0))
    plan = "monthly" if amount < 10000 else "yearly"

    if user_id and ref:
        grant_premium(user_id, plan_type=plan, payment_ref=ref)
        return jsonify({"status": "success"}), 200
    else:
        return jsonify({"status": "fail", "reason": "missing data"}), 400

if __name__ == "__main__":
    app.run(debug=True)
