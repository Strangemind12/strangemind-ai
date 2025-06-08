from flask import Blueprint, request, jsonify
from utils.google_scraper import google_direct_links
from utils.vault import shorten_link
from utils.youtube import youtube_search

commands = Blueprint("commands", __name__)

@commands.route("/search", methods=["POST"])
def handle_search():
    data = request.json
    phone = data.get("phone")
    text = data.get("message", "")
    query = text.replace("/search", "").strip()

    if not query:
        return jsonify({"reply": "❌ Usage: `/search movie name`"}), 200

    # 1. Get direct download links
    links = google_direct_links(query)
    links_output = "\n".join([f"🔗 [{l['title']}]({shorten_link(l['link'])})" for l in links]) or "No direct links found."

    # 2. Get YouTube trailers
    trailers = youtube_search(query)
    trailers_output = "\n".join([f"🎬 [{t['title']}]({t['url']})" for t in trailers]) or "No trailers found."

    reply = f"""🎥 *Search Results for:* `{query}`

{trailers_output}

📥 *Direct Download Links:*
{links_output}

💡 _Tap a link to open. Use responsibly!_
"""
    return jsonify({"reply": reply}), 200
