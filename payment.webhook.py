from flask import Flask, request, jsonify
from pymongo import MongoClient
import os

app = Flask(__name__)

MONGO_URI = os.getenv("MONGO_URI")
client = MongoClient(MONGO_URI)
db = client.strangemindDB
transactions_collection = db.transactions

@app.route("/webhook/payment-status", methods=["POST"])
def payment_status():
    data = request.json
    # Example payload keys: transaction_id, status, user_phone, amount, timestamp
    transaction_id = data.get("transaction_id")
    status = data.get("status")
    phone = data.get("user_phone")

    if not transaction_id or not status or not phone:
        return jsonify({"error": "Invalid data"}), 400

    # Update transaction record or insert if new
    transactions_collection.update_one(
        {"transaction_id": transaction_id},
        {"$set": {"status": status, "timestamp": data.get("timestamp")}},
        upsert=True,
    )

    # Optionally notify user or admin about status update
    # send_message(phone, f"Your transaction {transaction_id} status is now {status}")

    return jsonify({"message": "Webhook received"}), 200


if __name__ == "__main__":
    app.run(port=5001)
