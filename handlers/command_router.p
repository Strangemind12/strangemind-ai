from helpers.messaging import send_message
from commands.admin import handle_admin_command
from commands.user import handle_user_command

def route_message(phone, message, is_group=False, group_id=None, is_admin=False):
    message_lower = message.lower()

    if is_admin:
        handle_admin_command(phone, message, is_group, group_id)
    else:
        handle_user_command(phone, message, is_group, group_id)
