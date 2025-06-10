import requests
from config import SHORTIO_API_KEY, SHORTIO_DOMAIN

def monetize_link(original_url: str) -> str:
    """
    Shorten using Short.io API (free, ad-free clicks).
    """
    headers = {
        "Authorization": SHORTIO_API_KEY,
        "Content-Type": "application/json"
    }
    payload = {
        "originalURL": original_url,
        "domain": SHORTIO_DOMAIN
    }
    try:
        res = requests.post("https://api.short.io/links", json=payload, headers=headers, timeout=5)
        data = res.json()
        return data.get("shortURL") or data.get("shortPath") or original_url
    except Exception as e:
        print(f"[ERROR] monetize_link: {e}")
        return original_url
