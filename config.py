import os
from dotenv import load_dotenv

# Load variables from .env file
load_dotenv()

# === Gupshup WhatsApp API ===
GUPSHUP_API_KEY = os.getenv("GUPSHUP_API_KEY")

# === Bot Identity ===
BOT_NAME = os.getenv("BOT_NAME", "Strangemind AI")

# === OpenAI API (for text, memes, stories, etc.) ===
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

# === MongoDB Connection ===
MONGO_URI = os.getenv("MONGO_URI")

# === Admin contact (phone or email for privileged ops) ===
ADMIN_PHONE = os.getenv("ADMIN_PHONE")  # E.g. +23480125526502
ADMIN_EMAIL = os.getenv("ADMIN_EMAIL")

# === Feature toggles ===
ENABLE_PREMIUM = os.getenv("ENABLE_PREMIUM", "true").lower() == "true"
ENABLE_GAMIFIED_MODE = os.getenv("ENABLE_GAMIFIED_MODE", "true").lower() == "true"
ENABLE_MOVIE_ENGINE = os.getenv("ENABLE_MOVIE_ENGINE", "true").lower() == "true"
ENABLE_SPAM_FILTER = os.getenv("ENABLE_SPAM_FILTER", "true").lower() == "true"
WELCOME_ON_MENTION = os.getenv("WELCOME_ON_MENTION", "true").lower() == "true"

# === SMTP Email Settings for Admin Notifications ===
SMTP_SERVER = os.getenv("SMTP_SERVER")
SMTP_PORT = int(os.getenv("SMTP_PORT", "587"))
SMTP_USER = os.getenv("SMTP_USER")
SMTP_PASS = os.getenv("SMTP_PASS")

# === Other Constants ===
# Max message length, cooldowns, etc. can be added here if needed

# For debugging purposes, a quick print to verify (comment out in prod)
if __name__ == "__main__":
    print(f"Bot Name: {BOT_NAME}")
    print(f"Premium Enabled: {ENABLE_PREMIUM}")
    print(f"Movie Engine Enabled: {ENABLE_MOVIE_ENGINE}")# Config file for tokens and settings
