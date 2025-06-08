import os from pymongo import MongoClient from config import MONGO_URI, ADMIN_PHONE

MongoDB setup

client = MongoClient(MONGO_URI) db = client.strangemindDB users_collection = db.contacts groups_collection = db.groups  # Optional if you separate group logic premium_collection = db.premium_users

ADMIN_PHONE = ADMIN_PHONE.strip()

def is_admin(phone: str): """ Checks if the sender is the main admin. """ return phone == ADMIN_PHONE

def grant_premium(phone: str, is_group=False): """ Grants premium access to a user or group. """ collection = groups_collection if is_group else users_collection result = collection.update_one( {"phone": phone}, {"$set": {"is_premium": True}}, upsert=True ) # Also store in premium_collection for global tracking premium_collection.update_one( {"phone": phone}, {"$set": {"premium": True}}, upsert=True ) return result.modified_count > 0

def revoke_premium(phone: str, is_group=False): """ Revokes premium access from a user or group. """ collection = groups_collection if is_group else users_collection result = collection.update_one( {"phone": phone}, {"$set": {"is_premium": False}} ) premium_collection.update_one( {"phone": phone}, {"$set": {"premium": False}}, upsert=True ) return result.modified_count > 0

def check_premium(phone: str, is_group=False): """ Checks if a user or group has premium status. """ collection = groups_collection if is_group else users_collection record = collection.find_one({"phone": phone}) fallback = premium_collection.find_one({"phone": phone})

if record and record.get("is_premium", False):
    return True
elif fallback and fallback.get("premium", False):
    return True
return False

Example usage

if name == "main": test_user = "+2348012345678"

print("✅ Granting premium to test user...")
print(grant_premium(test_user))  # True if success

print("🔍 Checking premium status...")
print(check_premium(test_user))  # True

print("❌ Revoking premium...")
print(revoke_premium(test_user))  # True

print("🔍 Re-checking premium...")
print(check_premium(test_user))  # False

