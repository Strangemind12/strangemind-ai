from flask import Flask, request
from handlers.command_router import route_message

app = Flask(__name__)

@app.route('/webhook', methods=['POST'])
def webhook():
    data = request.json
    message = data.get("message")
    phone = data.get("phone")
    is_group = data.get("is_group", False)
    group_id = data.get("group_id")
    is_admin = phone == "YOUR_ADMIN_WHATSAPP_NUMBER"

    route_message(phone, message, is_group, group_id, is_admin)
    return "OK", 200

if __name__ == "__main__":
    app.run(port=5000)
