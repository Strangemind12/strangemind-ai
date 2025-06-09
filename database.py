from pymongo import MongoClient
from config import MONGO_URI

client = MongoClient(MONGO_URI)
db = client.strangemindDB

def get_all_users():
    return list(db.users.find())

def get_all_groups():
    return list(db.groups.find())

def set_autosave_flag(state: bool):
    db.config.update_one({"_id": "autosave"}, {"$set": {"enabled": state}}, upsert=True)

def get_autosave_flag() -> bool:
    config = db.config.find_one({"_id": "autosave"})
    return config.get("enabled", True)
