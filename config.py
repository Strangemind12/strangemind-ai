import os

GUPSHUP_API_KEY = os.getenv('GUPSHUP_API_KEY')
BOT_NAME = os.getenv('BOT_NAME', 'Strangemind AI')

# MongoDB URI
MONGO_URI = os.getenv('MONGO_URI')

# Premium and feature toggles
ENABLE_PREMIUM = os.getenv('ENABLE_PREMIUM', 'true').lower() == 'true'
ENABLE_GAMIFIED_MODE = os.getenv('ENABLE_GAMIFIED_MODE', 'true').lower() == 'true'

# Auto-save contacts
AUTO_SAVE_CONTACTS = os.getenv('AUTO_SAVE_CONTACTS', 'true').lower() == 'true'
AUTO_NAME_PREFIX = os.getenv('AUTO_NAME_PREFIX', 'Lead')
