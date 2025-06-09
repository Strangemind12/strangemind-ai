
from utils import is_user_vault_locked, is_group_vault_locked

def generate_short_link(original_url, user_id=None, group_id=None):
    # Check if user/group is locked from earning
    if user_id and is_user_vault_locked(user_id):
        return original_url  # No short link, earnings disabled
    
    if group_id and is_group_vault_locked(group_id):
        return original_url  # Group earning disabled
    
    # Else, shorten as usual
    return shorten_url_with_service(original_url)
