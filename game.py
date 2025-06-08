# game.py - Game logic for Strangemind AI

import datetime
from pymongo import MongoClient
from config import MONGO_URI

client = MongoClient(MONGO_URI)
db = client.strangemindDB
users = db.users

# 🎮 Create or get profile
def get_or_create_profile(phone):
    profile = users.find_one({"phone": phone})
    if not profile:
        profile = {
            "phone": phone,
            "xp": 0,
            "funds": 0,
            "level": 1,
            "last_played": None,
            "premium": False,
            "vault": 0,
            "withdraw_history": [],
        }
        users.insert_one(profile)
    return profile

# 💸 Add XP and funds
def earn_rewards(phone, xp_gain=10, fund_gain=5):
    profile = get_or_create_profile(phone)
    new_xp = profile["xp"] + xp_gain
    new_funds = profile["funds"] + fund_gain

    level = 1 + new_xp // 100  # Level up every 100 XP
    vault = profile.get("vault", 0) + fund_gain

    users.update_one(
        {"phone": phone},
        {
            "$set": {
                "xp": new_xp,
                "funds": new_funds,
                "level": level,
                "vault": vault,
                "last_played": datetime.datetime.utcnow(),
            }
        }
    )

# 🧾 Withdraw logic (Recharge Card or Mobile Money Placeholder)
def withdraw(phone, amount):
    profile = get_or_create_profile(phone)
    if profile["vault"] >= amount:
        users.update_one(
            {"phone": phone},
            {
                "$inc": {"vault": -amount},
                "$push": {
                    "withdraw_history": {
                        "amount": amount,
                        "timestamp": datetime.datetime.utcnow()
                    }
                }
            }
        )
        return True
    return False

# 🧑 Profile summary
def get_profile(phone):
    profile = get_or_create_profile(phone)
    return {
        "Level": profile["level"],
        "XP": profile["xp"],
        "Funds": profile["funds"],
        "Vault": profile["vault"],
        "Withdraws": len(profile["withdraw_history"]),
        "Premium": profile.get("premium", False),
    }

# 🔀 Commands
def handle_game_command(phone, text):
    text = text.strip().lower()
    if "/game" in text:
        earn_rewards(phone)
        return f"🎮 Game played! XP and funds added to your vault."
    elif "/withdraw" in text:
        if withdraw(phone, 50):  # Assume 50 as minimum withdraw unit
            return f"✅ Withdraw successful. Check your notifications!"
        else:
            return f"❌ Insufficient vault funds. Earn more by playing."
    elif "/profile" in text:
        profile = get_profile(phone)
        return (
            f"👤 Profile:\n"
            f"Level: {profile['Level']}\n"
            f"XP: {profile['XP']}\n"
            f"Vault: {profile['Vault']} credits\n"
            f"Withdrawals: {profile['Withdraws']}\n"
            f"Premium: {'Yes' if profile['Premium'] else 'No'}"
        )
    else:
        return None
