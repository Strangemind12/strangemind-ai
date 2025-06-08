strangemind_ai/premium_user_model.py

from datetime import datetime, timedelta from pymongo import MongoClient import os from flask import Flask, request, jsonify

MONGO_URI = os.getenv("MONGO_URI", "mongodb://localhost:27017/") client = MongoClient(MONGO_URI) db = client["strangemind"] premium_users = db["premium_users"]

Step 1: Create or update premium user

def create_premium_user(phone, plan_type="monthly", payment_ref=None): now = datetime.utcnow() expiry = now + timedelta(days=30 if plan_type == "monthly" else 365)

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

Step 2: Subscription checks

def is_premium(phone): user = premium_users.find_one({"phone": phone}) return bool(user and user.get("premium") and user.get("subscription_expiry") > datetime.utcnow())

def time_remaining(phone): user = premium_users.find_one({"phone": phone}) return user["subscription_expiry"] - datetime.utcnow() if user and user.get("subscription_expiry") else timedelta(0)

Step 3: Admin Commands

def grant_premium(phone, days): now = datetime.utcnow() expiry = now + timedelta(days=days) premium_users.update_one( {"phone": phone}, {"$set": { "premium": True, "subscription_start": now, "subscription_expiry": expiry, "payment_ref": "admin-granted", "last_payment": now }}, upsert=True ) return True

def revoke_premium(phone): premium_users.update_one({"phone": phone}, {"$set": {"premium": False}}) return True

Step 4: Decorator for Premium Features

def require_premium(func): def wrapper(phone, *args, **kwargs): if not is_premium(phone): return "⚠️ This feature is premium-only. Upgrade to access." return func(phone, *args, **kwargs) return wrapper

@require_premium def access_premium_feature(phone): return "🎉 Welcome to premium feature X!"

Optional: Webhook Listener

app = Flask(name)

@app.route('/api/payment-webhook', methods=['POST']) def payment_webhook(): data = request.json phone = data.get("phone") ref = data.get("reference") amount = data.get("amount") plan = "monthly" if amount < 10000 else "yearly"

if phone and ref:
    create_premium_user(phone, plan_type=plan, payment_ref=ref)
    return jsonify({"status": "success"}), 200
else:
    return jsonify({"status": "fail", "reason": "missing data"}), 400

if name == 'main': app.run(debug=True)

