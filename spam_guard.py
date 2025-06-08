from datetime import datetime, timedelta
from collections import defaultdict

# Memory map for rate limiting and behavior (replace with Redis/DB in prod)
message_history = defaultdict(list)

# Combine all spam keywords here
blacklist_words = [
    "scam", "fraud", "nude", "curseword1", "curseword2",
    "buy now", "free money", "click here", "subscribe", "cheap", "offer"
]

rate_limit_count = 5
rate_limit_seconds = 10

def is_spammy(message: str) -> bool:
    """
    Detect if the message contains any spam or blacklist keywords.
    Case-insensitive.
    """
    msg = message.lower()
    return any(word in msg for word in blacklist_words)

def is_rate_limited(phone: str) -> bool:
    """
    Checks if user is sending messages too fast (rate limiting).
    Allows `rate_limit_count` messages per `rate_limit_seconds`.
    """
    now = datetime.utcnow()
    recent = [t for t in message_history[phone] if now - t < timedelta(seconds=rate_limit_seconds)]
    message_history[phone] = recent + [now]
    return len(recent) > rate_limit_count

def detect_abuse(phone: str, message: str) -> str | None:
    """
    Returns warning messages if spammy or rate-limited.
    Otherwise returns None.
    """
    if is_spammy(message):
        return "🚫 Inappropriate or spammy language detected. Please follow the rules."
    if is_rate_limited(phone):
        return "🕒 You're messaging too fast. Please wait a moment."
    return None
