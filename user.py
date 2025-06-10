# handlers/user.py
from utils import send_message, monetize_link, is_autosave_enabled

from scraper import aggregate_search, youtube_search

import os

def handle_user_command(phone, message, is_group, group_id):
    msg = message.lower()

    if "@strangemind" in msg:
        send_message(phone, (
            "👋 Hi! I'm Strangemind AI.\n"
            "Commands:\n"
            "/help — this menu\n"
            "/movie <title>\n"
            "/search <title>\n"
            "/vault — show earnings\n"
            "/autosave — toggle contact autosave\n"
        ))
    elif msg.startswith("/help"):
        send_message(phone, "Available commands: /movie, /search, /vault, /autosave")
    elif msg.startswith("/autosave"):
        status = is_autosave_enabled(group_id if is_group else phone)
        send_message(phone, f"Auto-save is {'ON' if status else 'OFF'}. Use /autosave_on or /autosave_off.")
    elif msg.startswith("/movie "):
        query = message[7:].strip()
        results = aggregate_search(query, os.getenv("TMDB_API_KEY"))
        trailers = youtube_search(query, max_results=3, youtube_api_key=os.getenv("YOUTUBE_API_KEY"))
        reply = f"🎬 Results for \"{query}\":\n"
        for m in results[:3]:
            short_link = monetize_link(m["link"])
            reply += f"- {m['title']}: {short_link}\n"
        if trailers:
            reply += "\n🎥 Trailers:\n"
            reply += "\n".join(f"{t['url']}" for t in trailers)
        send_message(phone, reply)
    elif msg.startswith("/search "):
        query = message[8:].strip()
        results = aggregate_search(query, os.getenv("TMDB_API_KEY"))
        reply = "\n".join(f"{m['title']}: {monetize_link(m['link'])}" for m in results[:5])
        send_message(phone, reply or "No results found.")
    elif msg.startswith("/vault"):
        from utils import get_vault_balance
        bal = get_vault_balance(group_id if is_group else phone)
        send_message(phone, f"💰 Your vault balance: {bal}")
    else:
        send_message(phone, "🤖 Command not recognized. Send @strangemind or /help.")
