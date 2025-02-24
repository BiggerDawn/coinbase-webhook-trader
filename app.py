@app.route("/webhook", methods=["POST"])
def webhook():
    data = request.json
    if "action" in data and "ticker" in data and "size" in data:
        side = "buy" if data["action"] == "buy" else "sell"
        product_id = f"{data['ticker']}-USDC"  # Assuming USDC pairing
        size = data["size"]

        try:
            # 🔹 Fetch the current price from Coinbase
            product_info = client.get_product(product_id)
            current_price = float(product_info["price"])

            # 🔹 Set limit price closer to market price (0.1% instead of 1%)
            price_multiplier = 0.999 if side == "buy" else 1.001
            limit_price = round(current_price * price_multiplier, 6)  # 6 decimals for precision

            # 🔹 Place the limit order
            response = client.fiat_limit_buy(product_id, size, price=limit_price) if side == "buy" else client.fiat_limit_sell(product_id, size, price=limit_price)

            return jsonify(response), 200
        except Exception as e:
            return jsonify({"error": str(e)}), 500

    return jsonify({"error": "Invalid data"}), 400
