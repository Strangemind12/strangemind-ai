# referral.py
from datetime import datetime
from pymongo import MongoClient
from config import MONGO_URI

client = MongoClient(MONGO_URI)
db = client.strangemindDB
users = db.contacts
referrals = db.referrals

def create_referral(user_phone, ref_code):
    existing = referrals.find_one({"user": user_phone})
    if existing:
        return "⚠️ You’ve already used a referral code."

    if user_phone == ref_code:
        return "🤨 You can’t refer yourself, sly fox!"

    referrer = users.find_one({"phone": ref_code})
    if not referrer:
        return "❌ Invalid referral code."

    referrals.insert_one({
        "user": user_phone,
        "referrer": ref_code,
        "timestamp": datetime.utcnow()
    })

    users.update_one({"phone": ref_code}, {"$inc": {"ref_count": 1}}, upsert=True)
    users.update_one({"phone": user_phone}, {"$set": {"referred_by": ref_code}}, upsert=True)

    return "✅ Referral successful! Both of you get bonus coins 💰."

def get_my_referral_code(user_phone):
    return f"🧾 Your referral code is `{user_phone}`.\nAsk friends to send `/refer {user_phone}`."

def get_referral_rankings():
    top = users.find({"ref_count": {"$gt": 0}}).sort("ref_count", -1).limit(5)
    lines = ["🏆 *Top Referrers:*"]
    for idx, user in enumerate(top, 1):
        lines.append(f"{idx}. {user['phone']} — {user['ref_count']} refs")
    return "\n".join(lines) if lines else "📭 No referrals yet."

def get_referrer_info(user_phone):
    entry = referrals.find_one({"user": user_phone})
    if not entry:
        return "🔍 You haven’t been referred by anyone."
    return f"👥 You were referred by `{entry['referrer']}`."# Handles ranking logic
