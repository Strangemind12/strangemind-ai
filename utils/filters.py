# filters.py

import time
import re

# Simple in-memory store for rate limiting
rate_limit_cache = {}

# Cooldown in seconds
RATE_LIMIT_SECONDS = 10

# Common piracy terms to block
BLOCKED_KEYWORDS = [
    r"torrent",
    r"camrip",
    r"web[- ]?dl",
    r"hdcam",
    r"webrip",
    r"bluray",
    r"1080p",
    r"720p",
    r"dvdrip",
    r"x264",
    r"yify",
    r"brrip"
]

def is_blocked_query(query: str) -> bool:
    query = query.lower()
    for keyword in BLOCKED_KEYWORDS:
        if re.search(keyword, query):
            return True
    return False

def can_proceed(phone: str) -> bool:
    """
    Returns True if the user can send another request, False if rate limited.
    """
    now = time.time()
    last_time = rate_limit_cache.get(phone, 0)

    if now - last_time < RATE_LIMIT_SECONDS:
        return False

    rate_limit_cache[phone] = now
    return True
