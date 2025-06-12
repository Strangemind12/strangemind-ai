from your_original_bot_code import send_message  # Your actual function

def send_reply_to_whatsapp(chat_id, message):
    try:
        send_message(chat_id, message)
        return True
    except Exception as e:
        print(f"Error sending: {e}")
        return False
