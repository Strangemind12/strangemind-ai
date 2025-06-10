from helpers.consent import has_consented  # 👈 import your consent logic

def route_message(phone, message, is_group=False, group_id=None, is_admin=False):
    message_lower = message.lower()

    # 🚫 Meta-compliant group filter
    if is_group and not has_consented(phone):
        from helpers.messaging import send_message
        send_message(phone, "👋 Please DM me with /start to activate Strangemind AI.")
        return

    if is_admin:
        handle_admin_command(phone, message, is_group, group_id)
    else:
        handle_user_command(phone, message, is_group, group_id)
