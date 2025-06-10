import os
import requests

# 🔐 Secure your keys using environment variables
WHATSAPP_API_URL = os.getenv("WHATSAPP_API_URL", "https://your-whatsapp-api-url.com/send")
WHATSAPP_API_KEY = os.getenv("WHATSAPP_API_KEY", "your-api-key-here")

def send_message(phone: str, text: str) -> bool:
    """
    Sends a message to a WhatsApp user via API.
    
    Args:
        phone (str): WhatsApp phone number in international format.
        text (str): Message content.

    Returns:
        bool: True if sent successfully, False otherwise.
    """
    payload = {
        "phone": phone,
        "message": text,
        "key": WHATSAPP_API_KEY
    }
    try:
        response = requests.post(WHATSAPP_API_URL, json=payload, timeout=10)
        if response.status_code == 200:
            return True
        else:
            print(f"[ERROR] Failed to send message. Status: {response.status_code}, Response: {response.text}")
            return False
    except Exception as e:
        print(f"[ERROR] send_message: {e}")
        return False
