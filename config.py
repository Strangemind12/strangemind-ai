import os
from datetime import timedelta

# --- API Keys and Bot Settings ---
GUPSHUP_API_KEY = os.getenv('GUPSHUP_API_KEY')
WHATSAPP_API_KEY = os.getenv('WHATSAPP_API_KEY', '')  # Optional fallback
BOT_NAME = os.getenv('BOT_NAME', 'Strangemind AI')

# --- MongoDB Connection ---
MONGO_URI = os.getenv("MONGO_URI", "mongodb://localhost:27017/")  # Default local MongoDB URI

# --- Admin Controls ---
ADMIN_PHONE = os.getenv("ADMIN_PHONE", "+2348012345678")  # Default admin phone number placeholder

# --- Feature Toggles ---
ENABLE_PREMIUM = os.getenv('ENABLE_PREMIUM', 'true').lower() == 'true'
ENABLE_GAMIFIED_MODE = os.getenv('ENABLE_GAMIFIED_MODE', 'true').lower() == 'true'
AUTO_SAVE_CONTACTS = os.getenv('AUTO_SAVE_CONTACTS', 'true').lower() == 'true'
AUTO_NAME_PREFIX = os.getenv('AUTO_NAME_PREFIX', 'Lead')

# --- Premium Subscription Pricing (Nigerian Naira) ---
NIGERIA_MONTHLY_PRICE = float(os.getenv("NIGERIA_MONTHLY_PRICE", "5000.00"))  # Default ₦5,000/month
NIGERIA_YEARLY_PRICE = float(os.getenv("NIGERIA_YEARLY_PRICE", "18000.00"))  # Default ₦18,000/year (25% discount)

# --- Premium Subscription Duration ---
PREMIUM_MONTH_DURATION = timedelta(days=30)
PREMIUM_YEAR_DURATION = timedelta(days=365)

# --- Vault/Earnings System ---
VAULT_CURRENCY = "NGN"  # Nigerian Naira
ENABLE_VAULT = os.getenv('ENABLE_VAULT', 'true').lower() == 'true'
# config.py

MONGO_URI = "mongodb+srv://your_mongo_connection"
WHATSAPP_API_URL = "https://your-whatsapp-api-url.com/send"
WHATSAPP_API_KEY = "your-whatsapp-api-key"
SHRINK_LINK_API_KEY = "your_shrinkearn_api_key"
SHRINK_LINK_API = "https://api.shrinkearn.com/api"
ADMIN_PHONE_NUMBER = "234XXXXXXXXXX"  # Replace with real admin number
