from flask import Flask, request, jsonify
import os
from coinbase_advanced_trader.enhanced_rest_client import EnhancedRESTClient

app = Flask(__name__)

# Coinbase API Keys (Stored securely in Koyeb)
API_KEY = os.getenv("COINBASE_API_KEY")
API_SECRET = os.getenv("COINBASE_API_SECRET")

# Initialize the Coinbase Advanced Trade Client
client = EnhancedRESTClient(api_key=API_KEY, api_secret=API_SECRET)

@app.route("/", methods=["GET"])
def home():
    return "Webhook Server Running!", 200

@app.route("/webhook", methods=["POST"])
def webhook():
    data = request.json

    if "action" in data and "ticker" in data:
        side = "buy" if data["action"] == "buy" else "sell"
        product_id = f"{data['ticker']}-USD"  # Assuming USD pairing
        size = str(data.get("size", "10"))  # Default trade size: $10

        try:
            if side == "buy":
                response = client.fiat_market_buy(product_id, size)
            else:
                response = client.fiat_market_sell(product_id, size)

            return jsonify(response)
        except Exception as e:
            return jsonify({"error": str(e)}), 500

    return jsonify({"error": "Invalid data"}), 400

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
#test to see if the code works