# main.py
import os
from flask import Flask, request, jsonify
from handlers.command_router import route_message

app = Flask(__name__)

@app.route('/webhook', methods=['POST'])
def webhook():
    data = request.json
    phone    = data.get('from')
    message  = data.get('text', '')
    is_group = data.get('isGroup', False)
    group_id = data.get('group_id')

    is_admin = (phone == os.getenv("ADMIN_PHONE"))
    route_message(phone, message, is_group, group_id, is_admin)

    return jsonify({"status":"ok"}), 200

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=int(os.getenv("PORT", 5000)))
