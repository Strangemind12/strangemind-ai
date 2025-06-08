# strangemind_ai/spam_guard.py

from datetime import datetime, timedelta
from collections import defaultdict
import re

# Memory map for rate limiting and behavior (replace with Redis/DB in prod)
message_history = defaultdict(list)
blacklist_words = ["scam", "fraud", "nude", "curseword1", "curseword2"]
rate_limit_count = 5
rate_limit_seconds = 10

def is_spammy(message: str) -> bool:
    msg = message.lower()
    return any(word in msg for word in blacklist_words)

def is_rate_limited(phone: str) -> bool:
    now = datetime.utcnow()
    recent = [t for t in message_history[phone] if now - t < timedelta(seconds=rate_limit_seconds)]
    message_history[phone] = recent + [now]
    return len(recent) >= rate_limit_count

def detect_abuse(phone: str, message: str) -> str | None:
    if is_spammy(message):
        return "🚫 Inappropriate language detected. Please follow the rules."

    if is_rate_limited(phone):
        return "🕒 You're messaging too fast. Please wait a moment."

    return None
