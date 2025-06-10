import time

# Risky keywords to block (expand as needed)
BLOCKED_KEYWORDS = [
    "pirate", "torrent", "crack", "free download", "watch online", "full movie download",
    "mp4 download", "mkv download", "stream free", "hdmovie", "moviebox"
]

# Simple rate limiting (per phone)
user_last_request_time = {}

RATE_LIMIT_SECONDS = 5  # Example: 1 query every 5 seconds per user

def is_blocked_query(query):
    query_lower = query.lower()
    return any(kw in query_lower for kw in BLOCKED_KEYWORDS)

def can_proceed(phone):
    now = time.time()
    last_time = user_last_request_time.get(phone, 0)
    if now - last_time < RATE_LIMIT_SECONDS:
        return False
    user_last_request_time[phone] = now
    return True
