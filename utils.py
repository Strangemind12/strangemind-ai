import os import requests from bs4 import BeautifulSoup from datetime import datetime, timedelta from collections import defaultdict from pymongo import MongoClient from config import MONGO_URI, ADMIN_PHONE

--- MongoDB Setup ---

client = MongoClient(MONGO_URI) db = client.strangemindDB

Collections

vault_collection = db.vault users_collection = db.users history_collection = db.history groups_collection = db.groups  # Assuming groups_collection is also needed

--- Spam Guard Setup ---

message_history = defaultdict(list)

blacklist_words = [ "scam", "fraud", "nude", "curseword1", "curseword2", "buy now", "free money", "click here", "subscribe", "cheap", "offer" ]

rate_limit_count = 5 rate_limit_seconds = 10

def is_spammy(message: str) -> bool: msg = message.lower() return any(word in msg for word in blacklist_words)

def is_rate_limited(phone: str) -> bool: now = datetime.utcnow() recent = [t for t in message_history[phone] if now - t < timedelta(seconds=rate_limit_seconds)] message_history[phone] = recent + [now] return len(recent) >= rate_limit_count

def detect_abuse(phone: str, message: str) -> str | None: if is_spammy(message): return "\ud83d\udeab Inappropriate or spammy language detected. Please follow the rules." if is_rate_limited(phone): return "\ud83d\udd52 You're messaging too fast. Please wait a moment." return None

--- Vault Management ---

def shorten_link(url): api_key = os.getenv("SHRINKEARN_API_KEY") if not api_key: return url try: res = requests.get(f"https://shrinkearn.com/api?api={api_key}&url={url}") return res.json().get("shortenedUrl", url) except Exception as e: print("Shortener Error:", e) return url

def shorten_link_for_user(url, phone): short_url = shorten_link(url) vault_collection.update_one( {"user": phone}, {"$inc": {"clicks": 1}}, upsert=True ) return short_url

def get_vault_balance(phone: str) -> float: vault = vault_collection.find_one({"user": phone}) if vault: return vault.get("balance", 0) return 0

def withdraw_from_vault(phone: str, amount: float) -> bool: vault = vault_collection.find_one({"user": phone}) if vault and vault.get("balance", 0) >= amount: vault_collection.update_one({"user": phone}, {"$inc": {"balance": -amount}}) return True return False

def is_admin(phone: str) -> bool: if ADMIN_PHONE: return phone == ADMIN_PHONE return phone == "admin"

--- YouTube Search ---

YOUTUBE_API_KEY = os.getenv("YOUTUBE_API_KEY")

def youtube_search(query: str, max_results=3): if not YOUTUBE_API_KEY: return [{"url": f"https://youtube.com/watch?v=dQw4w9WgXcQ&search={query}"}]

url = "https://www.googleapis.com/youtube/v3/search"
params = {
    "part": "snippet",
    "q": query + " trailer",
    "key": YOUTUBE_API_KEY,
    "maxResults": max_results,
    "type": "video"
}
response = requests.get(url, params=params)
if response.status_code != 200:
    return []

items = response.json().get("items", [])
results = []
for item in items:
    video_id = item["id"]["videoId"]
    snippet = item["snippet"]
    results.append({
        "title": snippet["title"],
        "url": f"https://youtu.be/{video_id}",
        "channel": snippet.get("channelTitle", "Unknown"),
        "thumbnail": snippet["thumbnails"]["high"]["url"]
    })
return results

--- Contact & Activity Tracking ---

def save_contact(phone, name): existing = users_collection.find_one({"phone": phone}) if not existing: users_collection.insert_one({ "phone": phone, "name": name or "Unknown", "joined": datetime.utcnow(), "is_premium": False, "referral_code": None, "referred_by": None })

def save_activity(phone, action, data): history_collection.insert_one({ "phone": phone, "action": action, "data": data, "timestamp": datetime.utcnow() })

--- Google Scraper ---

def google_direct_links(query: str, limit: int = 5) -> list: search_query = f"{query} site:drive.google.com OR site:mediafire.com OR site:mega.nz download" headers = {"User-Agent": "Mozilla/5.0"} res = requests.get(f"https://www.google.com/search?q={search_query}", headers=headers) soup = BeautifulSoup(res.text, "html.parser")

results = []
for g in soup.select(".tF2Cxc"):
    link = g.select_one("a")
    title = g.select_one("h3")
    if link and title:
        results.append({"title": title.text.strip(), "link": link["href"]})
        if len(results) >= limit:
            break
return results

--- Admin Fetch Utilities ---

def get_all_users(): return list(users_collection.find({}, {"phone": 1}))

def get_all_groups(): return list(groups_collection.find({}, {"id": 1}))

