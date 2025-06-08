import datetime from pymongo import MongoClient from config import MONGO_URI

client = MongoClient(MONGO_URI) db = client.strangemindDB game_profiles = db.game_profiles

=== Game Settings ===

DEFAULT_VAULT_FUNDS = 0 DEFAULT_STATS = { "games_played": 0, "points": 0, "level": 1, "last_played": None, }

def get_user_game_profile(phone): profile = game_profiles.find_one({"phone": phone}) if not profile: profile = { "phone": phone, "vault": DEFAULT_VAULT_FUNDS, "stats": DEFAULT_STATS.copy(), "joined_at": datetime.datetime.utcnow(), "premium": False, } game_profiles.insert_one(profile) return profile

def update_game_stats(phone, points_earned): profile = get_user_game_profile(phone) new_points = profile["stats"].get("points", 0) + points_earned new_level = (new_points // 100) + 1

game_profiles.update_one(
    {"phone": phone},
    {"$set": {
        "stats.points": new_points,
        "stats.games_played": profile["stats"].get("games_played", 0) + 1,
        "stats.last_played": datetime.datetime.utcnow(),
        "stats.level": new_level,
    }}
)
return new_points, new_level

def add_funds_to_vault(phone, amount): game_profiles.update_one( {"phone": phone}, {"$inc": {"vault": amount}} )

def withdraw_funds(phone, method="recharge", destination=None): profile = get_user_game_profile(phone) balance = profile.get("vault", 0) if balance <= 0: return False, "Insufficient balance."

# TODO: connect to recharge API or payout system here

game_profiles.update_one(
    {"phone": phone},
    {"$set": {"vault": 0}}
)
return True, f"Withdrawal of ₦{balance} via {method} initiated."

def get_vault_balance(phone): profile = get_user_game_profile(phone) return profile.get("vault", 0)

def is_premium_user(phone): profile = get_user_game_profile(phone) return profile.get("premium", False)

def set_premium_status(phone, status: bool = True): game_profiles.update_one( {"phone": phone}, {"$set": {"premium": status}} )

=== Example CLI test ===

if name == "main": phone = "+2348012345678" print("[+] Starting game simulation for:", phone) profile = get_user_game_profile(phone) print("Current profile:", profile)

update_game_stats(phone, 50)
add_funds_to_vault(phone, 100)
print("Vault balance:", get_vault_balance(phone))

success, message = withdraw_funds(phone)
print(message)
print("Updated vault:", get_vault_balance(phone))

