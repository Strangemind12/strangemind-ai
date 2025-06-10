import requests

WHATSAPP_API_URL = "https://your-whatsapp-api-url.com/send"  # Replace with real URL
WHATSAPP_API_KEY = "your-api-key-here"

def send_message(phone: str, text: str) -> bool:
    """Sends a message to a WhatsApp user."""
    payload = {
        "phone": phone,
        "message": text,
        "key": WHATSAPP_API_KEY
    }
    try:
        response = requests.post(WHATSAPP_API_URL, json=payload)
        return response.status_code == 200
    except Exception as e:
        print(f"[ERROR] send_message: {e}")
        return False
