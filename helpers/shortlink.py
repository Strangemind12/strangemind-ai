import requests

SHORTLINK_API = "https://api.shrinkearn.com/api"
SHORTLINK_API_KEY = "your_shrinkearn_api_key"

def monetize_link(original_url: str) -> str:
    try:
        response = requests.get(f"{SHORTLINK_API}?api={SHORTLINK_API_KEY}&url={original_url}")
        data = response.json()
        return data.get("shortenedUrl", original_url)
    except Exception as e:
        print(f"[ERROR] monetize_link: {e}")
        return original_url
