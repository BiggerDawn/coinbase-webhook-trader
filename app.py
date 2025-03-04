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
        
        # Ensure ticker format is correct
        ticker = data["ticker"]
        if not ticker.endswith("-USDC"):  
            ticker = f"{ticker}-USDC"  

        try:
            # Fetch the current market price
            product_info = client.get_product(ticker)
            current_price = float(product_info["price"])

            # Calculate price_multiplier (1.0005 for buy, 0.9995 for sell)
            price_multiplier = 1.0005 if side == "buy" else 0.9995

            # Place limit order using price_multiplier
            if side == "buy":
                response = client.fiat_limit_buy(ticker, data["size"], price_multiplier=str(price_multiplier))
            else:
                # Retrieve full crypto balance for the given ticker to sell everything
                base_currency = ticker.split("-")[0]  # Extract "BTC" from "BTC-USDC"
                full_balance = client.get_crypto_balance(base_currency)
                response = client.fiat_limit_sell(ticker, str(full_balance), price_multiplier=str(price_multiplier))

            return jsonify(response), 200
        except Exception as e:
            return jsonify({"error": str(e)}), 500

    return jsonify({"error": "Invalid data"}), 400

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
