from flask import Flask, request, jsonify
import os
from coinbase_advanced_trader.enhanced_rest_client import EnhancedRESTClient

app = Flask(__name__)

# Load API credentials from environment variables
API_KEY = os.getenv("COINBASE_API_KEY")
API_SECRET = os.getenv("COINBASE_API_SECRET")

# Initialize Coinbase client
client = EnhancedRESTClient(api_key=API_KEY, api_secret=API_SECRET)

@app.route("/", methods=["GET"])
def home():
    return "Webhook Server Running!", 200

@app.route("/webhook", methods=["POST"])
def webhook():
    data = request.json
    if "action" in data and "ticker" in data and "size" in data:
        side = "buy" if data["action"] == "buy" else "sell"
        product_id = f"{data['ticker']}-USDC"  # Assuming USDC pairing
        size = data["size"]

        try:
            # Fetch the current market price
            product_info = client.get_product(product_id)
            current_price = float(product_info["price"])

            # Calculate price_multiplier (1.0005 for buy, 0.9995 for sell)
            price_multiplier = 1.0005 if side == "buy" else 0.9995

            # Place limit order using price_multiplier
            if side == "buy":
                response = client.fiat_limit_buy(product_id, size, price_multiplier=str(price_multiplier))
            else:
                response = client.fiat_limit_sell(product_id, size, price_multiplier=str(price_multiplier))

            return jsonify(response), 200
        except Exception as e:
            return jsonify({"error": str(e)}), 500

    return jsonify({"error": "Invalid data"}), 400

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)