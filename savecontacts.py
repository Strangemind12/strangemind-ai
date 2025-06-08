import datetime
import os
from pymongo import MongoClient
from config import MONGO_URI

# MongoDB setup
client = MongoClient(MONGO_URI)
db = client.strangemindDB
contacts_collection = db.contacts

def get_contact(phone: str):
    """
    Retrieves a user's contact info from the database.
    """
    return contacts_collection.find_one({"phone": phone})


def auto_generate_name(prefix="Lead"):
    """
    Generate next available contact name like Lead001, Lead002, etc.
    """
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
    """
    Saves or updates a user's contact in the database.
    Tracks premium users, last seen timestamp, and allows auto-naming.
    """
    existing = get_contact(phone)

    contact_data = {
        "last_seen": datetime.datetime.utcnow(),
        "is_premium": is_premium,
    }

    if name:
        contact_data["name"] = name

    # Handle new contact logic
    if not existing:
        contact_data["joined_at"] = datetime.datetime.utcnow()
        if os.getenv("AUTO_SAVE_CONTACTS", "false").lower() == "true":
            prefix = os.getenv("AUTO_NAME_PREFIX", "Lead")
            auto_name = auto_generate_name(prefix)
            contact_data["custom_name"] = auto_name
            print(f"[+] Auto-saved new contact: {phone} as {auto_name}")
        else:
            print(f"[+] New contact added: {phone}")
    else:
        print(f"[*] Contact updated: {phone}")

    contacts_collection.update_one(
        {"phone": phone},
        {"$set": contact_data},
        upsert=True
    )


def set_custom_name(phone: str, custom_name: str):
    """
    Sets a custom nickname or label for the contact.
    """
    result = contacts_collection.update_one(
        {"phone": phone},
        {"$set": {"custom_name": custom_name}}
    )
    return result.modified_count


def get_display_name(phone: str):
    """
    Returns custom name if set, else fallback to WhatsApp name or phone.
    """
    contact = get_contact(phone)
    if contact:
        return contact.get("custom_name") or contact.get("name") or phone
    return phone


# Example test (disable in production)
if __name__ == "__main__":
    test_phone = "+2348012345678"
    test_name = "WhatsApp User"

    save_or_update_contact(test_phone, test_name, is_premium=True)
    user_data = get_contact(test_phone)
    print(f"User data: {user_data}")
    print(f"Display name: {get_display_name(test_phone)}")# Google contact sync logic
