def notify_admin(user_phone, message):
    admin_number = "admin-whatsapp-number"  # or os.getenv("ADMIN_PHONE")
    print(f"[ALERT] Admin notified about {user_phone}: {message}")
    # You could plug in WhatsApp API send here if needed
