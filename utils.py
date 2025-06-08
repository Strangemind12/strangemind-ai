from flask import Flask, request, jsonify
from scraper import aggregate_search
from utils import shorten_link, is_premium_user, is_admin, get_vault_balance, withdraw_from_vault
import os

app = Flask(__name__)
TMDB_API_KEY = os.getenv("TMDB_API_KEY")

@app.route('/search', methods=['GET'])
def search_movie():
    query = request.args.get('query')
    if not query:
        return jsonify({"error": "Missing 'query' parameter"}), 400

    raw_results = aggregate_search(query, tmdb_api_key=TMDB_API_KEY)
    monetized_results = []
    for item in raw_results:
        short_link = shorten_link(item['link'])
        monetized_results.append({
            "title": item.get('title', 'No Title'),
            "link": short_link,
            "source": item.get('source', 'Unknown')
        })

    return jsonify({"results": monetized_results})


# Optional: example admin vault check endpoint
@app.route('/vault/balance', methods=['GET'])
def vault_balance():
    phone = request.args.get('phone')
    if not phone or not is_admin(phone):
        return jsonify({"error": "Unauthorized or missing phone parameter"}), 403
    balance = get_vault_balance()
    return jsonify({"vault_balance": balance})


# Optional: admin vault withdraw endpoint
@app.route('/vault/withdraw', methods=['POST'])
def vault_withdraw():
    data = request.json
    phone = data.get('phone')
    amount = data.get('amount')
    if not phone or not is_admin(phone):
        return jsonify({"error": "Unauthorized"}), 403
    if not amount or amount <= 0:
        return jsonify({"error": "Invalid amount"}), 400
    success = withdraw_from_vault(amount)
    if not success:
        return jsonify({"error": "Insufficient balance"}), 400
    return jsonify({"message": f"Successfully withdrew {amount} units from vault."})


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8080)
