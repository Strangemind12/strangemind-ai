from pymongo import MongoClient
from config import MONGO_URI

# MongoDB setup
client = MongoClient(MONGO_URI)
db = client.strangemindDB
locks_collection = db.locks

def is_locked(entity_type: str, entity_id: str) -> bool:
    """
    Check if a user, group, or member is locked.
    entity_type: "user", "group", or "member"
    entity_id: phone number or group id string
    """
    lock = locks_collection.find_one({"type": entity_type, "id": entity_id})
    return lock.get("locked", False) if lock else False

def set_lock(entity_type: str, entity_id: str, locked: bool) -> None:
    """
    Lock or unlock an entity.
    """
    locks_collection.update_one(
        {"type": entity_type, "id": entity_id},
        {"$set": {"locked": locked}},
        upsert=True
    )

def get_display_balance(phone: str, get_vault_balance_func, group_id: str = None, member_phone: str = None) -> float:
    """
    Get vault balance respecting locks.
    get_vault_balance_func: function to fetch actual balance from DB
    """
    if is_locked("user", phone):
        return 0.0
    if group_id and is_locked("group", group_id):
        return 0.0
    if member_phone and is_locked("member", member_phone):
        return 0.0
    return get_vault_balance_func(phone)

def handle_admin_lock_command(command: str, entity_type: str, entity_id: str) -> str:
    """
    Handle lock/unlock commands from admin.
    command: "lock" or "unlock"
    entity_type: "user", "group", or "member"
    entity_id: identifier string
    """
    locked = (command == "lock")
    set_lock(entity_type, entity_id, locked)
    status = "locked 🔒" if locked else "unlocked 🔓"
    return f"{entity_type.capitalize()} '{entity_id}' has been {status} successfully."

def format_earnings_response(balance: float) -> str:
    """
    Format earnings message with placeholder if zero (locked).
    """
    if balance == 0.0:
        return (
            "💰 Your vault balance: ₦000.00\n"
            "🚫 Earnings locked or unavailable.\n"
            "Please contact admin for details."
        )
    else:
        return (
            f"💰 Your vault balance: ₦{balance:.2f}\n"
            "🚧 Withdrawals & earnings feature coming soon! Stay tuned."
        )

from locks_manager import (
    is_locked, set_lock, get_display_balance, 
    handle_admin_lock_command, format_earnings_response
                                      )
