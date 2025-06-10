from helpers.messaging import send_message
from helpers.autosave import is_autosave_enabled
from helpers.shortlink import monetize_link

def handle_user_command(phone, message, is_group, group_id):
    if "@strangemind" in message.lower():
        response = "👋 Hello! I'm Strangemind AI. Type /help to see commands."
        send_message(phone, response)
    elif "/help" in message:
        send_message(phone, "📘 Commands: /movie, /autosave, /rank, /vault, /referral")
    elif "/autosave" in message:
        status = is_autosave_enabled(phone)
        send_message(phone, f"📲 Autosave is currently {'enabled' if status else 'disabled'}")
    elif "/movie" in message:
        movie_link = "https://example.com/movies/spiderman"
        monetized_link = monetize_link(movie_link)
        send_message(phone, f"🎬 Movie link: {monetized_link}")
    else:
        send_message(phone, "🤖 Command not recognized. Try /help.")
