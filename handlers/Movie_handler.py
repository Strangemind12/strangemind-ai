# handlers/movie_handler.py

import logging
import requests
from urllib.parse import quote_plus
from utils.sender import send_message
from filters import is_blocked_query, can_proceed

# Configure logging
logging.basicConfig(filename='strangemind_ai.log', level=logging.INFO)

# Short.io Config (replace with your actual keys/domain)
SHORT_IO_API = "https://api.short.io/links"
SHORT_IO_API_KEY = "YOUR_SHORT_IO_API_KEY"
SHORT_IO_DOMAIN = "your.custom.domain"  # e.g., "strangemind.link"

def shorten_url(long_url):
    payload = {
        "originalURL": long_url,
        "domain": SHORT_IO_DOMAIN
    }
    headers = {
        "Authorization": SHORT_IO_API_KEY,
        "Content-Type": "application/json"
    }
    try:
        response = requests.post(SHORT_IO_API, json=payload, headers=headers, timeout=5)
        if response.status_code == 201:
            return response.json().get("shortURL")
    except Exception as e:
        logging.error(f"Short.io API error: {e}")
    return long_url  # fallback if shortening fails

def handle_movie_command(phone, query):
    query = query.strip()

    # Check if query is blocked
    if is_blocked_query(query):
        send_message(phone, "⚠️ Sorry, your search term may involve copyrighted or illegal content which we do not support. Please search for legal content only.")
        logging.info(f"Blocked illegal search query from {phone}: {query}")
        return

    # Check rate limiting
    if not can_proceed(phone):
        send_message(phone, "⏳ Slow down! Please wait a few seconds before sending another query.")
        logging.info(f"Rate limit hit for {phone}")
        return

    # Encode and generate URLs
    encoded_query = quote_plus(query)
    google_search_url = f"https://www.google.com/search?q=download+{encoded_query}+site:archive.org"
    external_search_url = f"https://strangemind-movies.koyeb.com/?q={encoded_query}"

    # Shorten both links
    short_google_url = shorten_url(google_search_url)
    short_external_url = shorten_url(external_search_url)

    # Build the message
    disclaimer = (
        "⚠️ *Disclaimer:* Strangemind AI doesn’t host or distribute any movies. "
        "Links lead to public search results only. Use responsibly.\n"
        "📚 *Note:* Piracy is illegal. Support creators by accessing legal content."
    )

    message = (
        f"🎬 *Movie Lookup: {query}*\n"
        f"🔍 Google Search: {short_google_url}\n"
        f"🔗 External Link (safe): {short_external_url}\n\n"
        f"{disclaimer}"
    )

    send_message(phone, message)
    logging.info(f"Movie search for '{query}' sent to {phone}")
