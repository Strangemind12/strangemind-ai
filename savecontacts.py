import datetime
from pymongo import MongoClient
from config import MONGO_URI, AUTO_SAVE_CONTACTS, AUTO_NAME_PREFIX

client = MongoClient(MONGO_URI)
db = client.strangemindDB
contacts_collection = db.contacts


def get_contact(phone: str):
    return contacts_collection.find_one({"phone": phone})


def auto_generate_name(prefix=AUTO_NAME_PREFIX):
    existing = contacts_collection.find(
        {"custom_name": {"$regex": f"^{prefix}\\d+$"}}
    ).sort("custom_name", -1).limit(1)

    latest = list(existing)
    if latest:
        try:
            last_num = int(latest[0]["custom_name"].replace(prefix, ""))
        except ValueError:
            last_num = 0
        return f"{prefix}{last_num + 1:03d}"
    else:
        return f"{prefix}001"


def save_or_update_contact(phone: str, name: str = None, is_premium: bool = False):
    existing = get_contact(phone)
    contact_data = {
        "last_seen": datetime.datetime.utcnow(),
        "is_premium": is_premium,
    }
    if name:
        contact_data["name"] = name

    if not existing and AUTO_SAVE_CONTACTS:
        contact_data["joined_at"] = datetime.datetime.utcnow()
        prefix = AUTO_NAME_PREFIX
        auto_name = auto_generate_name(prefix)
        contact_data["custom_name"] = auto_name

    contacts_collection.update_one(
        {"phone": phone},
        {"$set": contact_data},
        upsert=True
    )


def set_custom_name(phone: str, custom_name: str):
    result = contacts_collection.update_one(
        {"phone": phone},
        {"$set": {"custom_name": custom_name}}
    )
    return result.modified_count


def get_display_name(phone: str):
    contact = get_contact(phone)
    if contact:
        return contact.get("custom_name") or contact.get("name") or phone
    return phone
