from urllib.parse import quote_plus
from utils.messaging import send_message  # Adjust if your send_message is elsewhere

def handle_movie_command(phone, query):
    encoded_query = quote_plus(query.strip())

    google_search_url = f"https://www.google.com/search?q=download+{encoded_query}+site:archive.org"
    external_search_url = f"https://strangemind-movies.koyeb.com/?q={encoded_query}"

    disclaimer = (
        "⚠️ *Disclaimer:* Strangemind AI doesn’t host or distribute any movies. "
        "Results are from public search engines. Use responsibly."
    )

    message = (
        f"🎬 *Movie Lookup: {query}*\n"
        f"🔍 Google Search: {google_search_url}\n"
        f"🔗 External Link (safe): {external_search_url}\n\n"
        f"{disclaimer}"
    )

    send_message(phone, message)
