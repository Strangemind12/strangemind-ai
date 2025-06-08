import os
from flask import Flask, request, jsonify
from config import GUPSHUP_API_KEY, BOT_NAME
from savecontacts import save_or_update_contact, get_display_name
from autoreply import handle_auto_reply
from utils import is_premium_user, send_message

app = Flask(__name__)

@app.route('/webhook', methods=['POST'])
def webhook():
    data = request.json
    phone = data.get('from')
    message = data.get('text')
    is_group = data.get('isGroup', False)
    group_id = data.get('groupId') if is_group else None

    # Check if user/group is premium for auto-save
    if is_premium_user(phone if not is_group else group_id):
        save_or_update_contact(phone, is_premium=True)

    # Handle autoreply based on individual/group
    reply = handle_auto_reply(phone, message, is_group, group_id)
    if reply:
        send_message(phone if not is_group else group_id, reply)

    return jsonify({"status": "success"}), 200


if __name__ == '__main__':
    port = int(os.getenv('PORT', 5000))
    app.run(host='0.0.0.0', port=port)
