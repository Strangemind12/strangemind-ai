# utils.py
import os, requests
from pymongo import MongoClient
from collections import defaultdict
from datetime import datetime, timedelta

client = MongoClient(os.getenv("MONGO_URI"))
db = client.strangemindDB

vault_col    = db.vault
autosave_col = db.autosave_settings

message_history = defaultdict(list)
blacklist = ["scam","buy now","free money","click here"]
RATE_LIMIT, RATE_SECONDS = 5, 10

def send_message(phone,text):
    print(f"[SEND] To {phone}: {text}")  # Replace with real API call

def monetize_link(url):
    key = os.getenv("SHRINKEARN_API_KEY")
    try:
        res = requests.get(f"https://shrinkearn.com/api?api={key}&url={url}")
        return res.json().get("shortenedUrl", url)
    except:
        return url

def is_spammy(msg):
    return any(w in msg.lower() for w in blacklist)

def is_rate_limited(phone):
    now = datetime.utcnow()
    recent = [t for t in message_history[phone] if (now - t).seconds < RATE_SECONDS]
    message_history[phone] = recent + [now]
    return len(recent) >= RATE_LIMIT

def lock_earnings(user_or_group):
    vault_col.update_one({"user": user_or_group}, {"$set":{"locked":True}}, upsert=True)

def unlock_earnings(user_or_group):
    vault_col.update_one({"user": user_or_group}, {"$set":{"locked":False}}, upsert=True)

def get_vault_balance(user_or_group):
    rec = vault_col.find_one({"user": user_or_group}) or {}
    return rec.get("balance", 0)

def withdraw_from_vault(user_or_group, amount):
    rec = vault_col.find_one({"user": user_or_group})
    if rec and rec.get("balance",0) >= amount and not rec.get("locked"):
        vault_col.update_one({"user": user_or_group}, {"$inc":{"balance":-amount}})
        return True
    return False

def is_autosave_enabled(user_or_group):
    rec = autosave_col.find_one({"user":user_or_group})
    return bool(rec and rec.get("enabled",False))

def set_autosave(user_or_group, status:bool):
    autosave_col.update_one({"user": user_or_group}, {"$set":{"enabled": status}}, upsert=True)
