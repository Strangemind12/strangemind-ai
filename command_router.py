from helpers.consent import has_consented

def route_message(phone, message, is_group=False, group_id=None, is_admin=False):
    if is_group and not has_consented(phone):
        return  # Ignore unsolicited group messages

    if is_admin:
        handle_admin_command(phone, message, is_group, group_id)
    else:
        handle_user_command(phone, message, is_group, group_id)
