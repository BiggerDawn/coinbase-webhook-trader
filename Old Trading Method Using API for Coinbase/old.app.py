from flask import Flask, request, jsonify
import requests
import os

app = Flask(__name__)

# Coinbase API Keys (Use Koyeb secrets instead of hardcoding these)
COINBASE_API_KEY = os.getenv("COINBASE_API_KEY")
COINBASE_API_SECRET = os.getenv("COINBASE_API_SECRET")
COINBASE_API_URL = "https://api.coinbase.com/v2/orders"  # Adjust if using Advanced Trade API

def place_order(side, product_id, size):
    """Places an order on Coinbase"""
    headers = {
        "CB-ACCESS-KEY": COINBASE_API_KEY,
        "CB-ACCESS-SIGN": COINBASE_API_SECRET,
        "Content-Type": "application/json",
    }
    data = {
        "side": side,
        "product_id": product_id,  # e.g., "BTC-USD"
        "size": size,  # Amount to buy/sell
        "type": "market",  # You can change to limit
    }
    response = requests.post(COINBASE_API_URL, json=data, headers=headers)
    return response.json()

@app.route("/", methods=["GET"])
def home():
    return "Webhook Server Running!", 200

@app.route("/webhook", methods=["POST"])
def webhook():
    data = request.json
    if "action" in data and "ticker" in data:
        side = "buy" if data["action"] == "buy" else "sell"
        product_id = f"{data['ticker']}-USD"  # Assuming USD pairing
        size = data.get("size", 0.01)  # Default trade size
        response = place_order(side, product_id, size)
        return jsonify(response)
    return jsonify({"error": "Invalid data"}), 400

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
