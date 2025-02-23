from flask import Flask, request, jsonify
from coinbase_advanced_trader.enhanced_rest_client import EnhancedRESTClient
import os
import hmac
import hashlib

app = Flask(__name__)

# Initialize Coinbase client
client = EnhancedRESTClient(
    api_key=os.getenv('COINBASE_API_KEY'),
    api_secret=os.getenv('COINBASE_API_SECRET')
)

# Get webhook secret from environment
WEBHOOK_SECRET = os.getenv('TRADINGVIEW_SECRET')

@app.route('/webhook', methods=['POST'])
def handle_webhook():
    try:
        # Verify signature
        signature = request.headers.get('tv-signature')
        payload = request.get_data(as_text=True)
        
        if not verify_signature(payload, signature):
            return jsonify({"status": "error", "message": "Invalid signature"}), 401

        data = request.json
        action = data.get('action').lower()
        product_id = data.get('product_id')
        amount = data.get('amount')
        order_type = data.get('type', 'market').lower()

        # Execute trade
        if action == 'buy':
            if order_type == 'market':
                result = client.fiat_market_buy(product_id, amount)
            elif order_type == 'limit':
                price = data.get('price')
                result = client.fiat_limit_buy(product_id, amount, price)
        elif action == 'sell':
            if order_type == 'market':
                result = client.fiat_market_sell(product_id, amount)
            elif order_type == 'limit':
                price = data.get('price')
                result = client.fiat_limit_sell(product_id, amount, price)
        else:
            return jsonify({"status": "error", "message": "Invalid action"}), 400

        return jsonify({"status": "success", "result": result}), 200

    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500

def verify_signature(payload, signature):
    if not WEBHOOK_SECRET or not signature:
        return False
    digest = hmac.new(WEBHOOK_SECRET.encode(), msg=payload.encode(), digestmod=hashlib.sha256).hexdigest()
    return hmac.compare_digest(digest, signature)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=int(os.getenv('PORT', 5000)))