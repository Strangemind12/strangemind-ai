from helpers.consent import has_consented  # 👈 Make sure this import is at the top

def route_message(phone, message, is_group=False, group_id=None, is_admin=False):
    message_lower = message.lower()

    if is_group and not has_consented(phone):
        send_message(phone, "👋 Please DM me with /start to activate Strangemind AI.")
        return  # 🔒 Block further processing unless user opts in

    if is_admin:
        handle_admin_command(phone, message, is_group, group_id)
    else:
        handle_user_command(phone, message, is_group, group_id)
