from flask import Flask, request, jsonify
import hmac
import hashlib
import os

app = Flask(__name__)

# Your Coinbase webhook secret (Get this from Coinbase Webhook Portal)
COINBASE_WEBHOOK_SECRET = os.getenv("COINBASE_WEBHOOK_SECRET")

def verify_coinbase_signature(request):
    """Verifies the HMAC-SHA256 signature from Coinbase to ensure it's authentic."""
    signature = request.headers.get("x-coinbase-signature")
    if not signature:
        return False

    # Coinbase sends the webhook ID as the key, request body as payload
    webhook_id = COINBASE_WEBHOOK_SECRET.encode('utf-8')
    payload = request.data  # Raw request body
    
    # Generate HMAC signature
    h = hmac.new(webhook_id, payload, hashlib.sha256)
    
    # Compare the expected vs calculated signatures
    return hmac.compare_digest(h.hexdigest(), signature)

@app.route("/", methods=["GET"])
def home():
    return "Coinbase Webhook Listener Running!", 200

@app.route("/coinbase-webhook", methods=["POST"])
def coinbase_webhook():
    """Handles incoming Coinbase webhook events"""
    if not verify_coinbase_signature(request):
        return jsonify({"error": "Unauthorized"}), 401

    data = request.json
    print("Received Coinbase Webhook:", data)  # Debugging Log
    
    event_type = data.get("eventType", "")

    if event_type == "transaction":
        # Here, you can trigger any logic you want
        print(f"Trade executed: {data}")
        return jsonify({"message": "Trade processed"}), 200

    return jsonify({"message": "Event received"}), 200

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)