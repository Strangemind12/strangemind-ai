import os
import requests

YOUTUBE_API_KEY = os.getenv("YOUTUBE_API_KEY")

def shorten_link(long_url):
    # Placeholder: add monetized shortener here
    return long_url

def is_premium_user(phone):
    # Replace with real logic
    return phone and phone.endswith("7")  # Just a dummy rule

def is_admin(phone):
    # Replace with real logic
    return phone == "admin"

def get_vault_balance():
    # Simulate balance check
    return 9999

def withdraw_from_vault(amount):
    # Simulate vault withdrawal logic
    if amount > 9999:
        return False
    return True

def youtube_search(query, max_results=3):
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
