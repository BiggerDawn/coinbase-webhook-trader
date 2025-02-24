from flask import Flask, request, jsonify
import os
from coinbase_advanced_trader.enhanced_rest_client import EnhancedRESTClient

app = Flask(__name__)  # ✅ Ensure Flask app is defined first

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
        side = "BUY" if data["action"] == "buy" else "SELL"
        product_id = f"{data['ticker']}-USDC"  # Assuming USDC pairing
        size = data["size"]

        try:
            # 🔹 Fetch the current market price
            product_info = client.get_product(product_id)
            current_price = float(product_info["price"])

            # 🔹 Adjust the limit price closer to market price
            price_multiplier = 0.999 if side == "BUY" else 1.001
            limit_price = round(current_price * price_multiplier, 6)  # 6 decimal places

            # 🔹 Place the limit order using create_limit_order()
            response = client.create_limit_order(
                product_id=product_id,
                side=side,
                order_configuration={
                    "limit_limit_gtc": {
                        "base_size": str(size),
                        "limit_price": str(limit_price)
                    }
                }
            )

            return jsonify(response), 200
        except Exception as e:
            return jsonify({"error": str(e)}), 500

    return jsonify({"error": "Invalid data"}), 400

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
