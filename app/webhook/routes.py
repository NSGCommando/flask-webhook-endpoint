from flask import Blueprint, jsonify, request

webhook = Blueprint('Webhook', __name__, url_prefix='/webhook')

@webhook.route('/receiver', methods=["POST"])
def receiver():
    data =request.get_json(silent=True) # use get_json() to handle possible empty responses
    if not data:
        return jsonify({"error": "No JSON payload received"}), 400
    
    print("Received webhook data:", data)
    return jsonify({"status": "received"}), 200
