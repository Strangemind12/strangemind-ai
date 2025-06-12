# message_sender.py

# === START WITH MOCK ===
USE_MOCK = True  # 🔄 Change this to False to go live later

def mock_send_message(chat_id, message):
    print(f"[MOCK] Message to {chat_id}: {message}")
    return True

# Placeholder for the real function (future-proofed)
try:
    if not USE_MOCK:
        from whatsapp_bot import send_message  # ⬅️ Replace with your real sender file & function
    else:
        send_message = mock_send_message
except ImportError:
    print("⚠️ Real sender not found. Using mock mode.")
    send_message = mock_send_message


def send_reply_to_whatsapp(chat_id, message):
    try:
        send_message(chat_id, message)
        return True
    except Exception as e:
        print(f"❌ Failed to send message: {e}")
        return False
