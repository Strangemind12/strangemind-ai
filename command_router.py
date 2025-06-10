# handlers/command_router.py
from commands.admin import handle_admin_command
from commands.user  import handle_user_command

def route_message(phone, message, is_group, group_id, is_admin):
    if is_admin:
        handle_admin_command(phone, message, is_group, group_id)
    else:
        handle_user_command(phone, message, is_group, group_id)
