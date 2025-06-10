from pymongo import MongoClient

client = MongoClient("mongodb+srv://your_mongo_url")
db = client["strangemind_ai"]
consent_collection = db["consent"]

def has_consented(phone: str) -> bool:
    user = consent_collection.find_one({"phone": phone})
    return user.get("consented", False) if user else False

def set_consent(phone: str, status: bool):
    consent_collection.update_one(
        {"phone": phone},
        {"$set": {"consented": status}},
        upsert=True
    )
