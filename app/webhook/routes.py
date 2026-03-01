from flask import Blueprint, jsonify, request, render_template, abort
from app.project_logger import project_logger # need to run from project root for absolute imports to work
from app.extensions import mongo
import hmac, hashlib, os
from datetime import datetime, timezone

SECRET = os.getenv("SECRET_KEY")
webhook = Blueprint('Webhook', __name__, url_prefix='/webhook')

@webhook.route('/receiver', methods=["POST"])
def receiver():
    data = request.get_json(silent=True) # use get_json() to handle possible empty responses
    if not data:
        project_logger.warning("No event JSON received")
        return jsonify({"error": "No JSON payload received"}), 400
    # handle security checks
    if not SECRET:
        project_logger.critical("SECRET_KEY is not set in environment variables!")
        raise ValueError("No SECRET_KEY set for Webhook verification. Check your .env file.")
    if mongo.db is None:
        raise RuntimeError("Mongo DB has not been initialized")
    # get webhook signature
    signature = request.headers.get("X-Hub-Signature-256")
    if not signature:
        project_logger.error("Missing Signature")
        abort(400, "Missing Signature") 
    # store webhook hash
    sha_name, signature_hash = signature.split('=')
    if sha_name != 'sha256':
        project_logger.error("Unsupported hash algorithm")
        abort(400, "Unsupported hash algorithm")
    # generate local hash via hexdigest
    local_hash = hmac.new(
        SECRET.encode('utf-8'), 
        msg=request.get_data(), 
        digestmod=hashlib.sha256
    ).hexdigest()

    # Compare hashes via comparing the digest to prevent timing attacks
    if not hmac.compare_digest(local_hash, signature_hash):
        project_logger.error("Invalid webhook signature")
        abort(401, "Invalid signature")
    
    # security verified, handle response JSON 
    event = request.headers.get('X-GitHub-Event')
    project_logger.info(f"Webhook verified! Event: {event}")
    if event == "ping":
        return jsonify({"status": "pong"}), 200
    pr_data = data.get("pull_request", {}) # extract pull request
    pr_action = data.get("action")
    is_merged = pr_data.get("merged", False) # default to False if not found
    # compile all relevant data
    log_doc={
                "request_id": "",
                "author": "",
                "action": "",
                "from_branch": "N/A",
                "to_branch": "",
                "timestamp": ""
            }

    # Push event
    if event == "push":
        log_doc["action"] = "PUSH"
        author = data.get("sender", {}).get("login")
        log_doc["author"] = author
        log_doc["request_id"] = data.get("after")
        if log_doc["request_id"] == "0000000000000000000000000000000000000000":
            project_logger.info("Branch deletion detected. Skipping processing.")
            return jsonify({"status": "ignored"}), 200
        log_doc["to_branch"] = data.get("ref", "").replace("refs/heads/", "")

        raw_time = data.get("repository", {}).get("pushed_at") 
        # Convert to string(datetime) format: "YYYY-MM-DD HH:MM:SS"
        if isinstance(raw_time, (int, float)):
            dt_object = datetime.fromtimestamp(raw_time, tz=timezone.utc)
            received_timestamp = dt_object.strftime('%Y-%m-%d %H:%M:%S UTC') # Format to ISO 8601 / UTC standard
        else:
            received_timestamp = str(raw_time) # Fallback cast
        log_doc["timestamp"] = received_timestamp
        project_logger.info("[Push] Author: %s, Timestamp: %s", author, received_timestamp)

    # Pull request event
    elif event == "pull_request":
        log_doc["request_id"] = str(pr_data.get("id"))
        author = pr_data.get("user", {}).get("login")
        log_doc["author"]= author
        pr_from = pr_data.get("head", {}).get("ref") # The source branch
        pr_to = pr_data.get("base", {}).get("ref") # The destination branch
        log_doc["to_branch"] = pr_to
        log_doc["from_branch"] = pr_from
        received_timestamp = pr_data.get("updated_at")
        log_doc["timestamp"] = received_timestamp
        # check for merged request or not
        if pr_action == "closed" and is_merged:
            log_doc["action"] = "MERGE"
            project_logger.info(
                "[Pull Request Merged] Action: %s, From: %s, To: %s, author: %s, Merge Time:%s",
                pr_action,pr_from,pr_to,author,received_timestamp
            )
        else:
            log_doc["action"] = "PULL_REQUEST"
            project_logger.info(
                "[Pull Request] Action: %s, From: %s, To: %s, author: %s",
                pr_action,pr_from,pr_to,author
            )
    else:
        project_logger.warning("[WARNING] Unkwown Request")

    if event in ("push","pull_request"):
        mongo.db["webhook_logs"].insert_one(log_doc)
    project_logger.info("Received Request")
    return jsonify({"status": "received"}), 200

@webhook.route('/dashboard')
def show_dashboard():
    # Load the main shell of the page
    return render_template('dashboard.html')

@webhook.route('/actions-data')
def actions_data():
    if mongo.db is None:
        raise RuntimeError("Mongo DB has not been initialized")
    actions_cursor = mongo.db["webhook_logs"].find().sort('_id', -1).limit(10)
    actions = list(actions_cursor) # Convert cursor to a list
    return render_template('_action_list.html', actions=actions)