from flask import Blueprint, jsonify, request, render_template
from app.project_logger import project_logger # need to run from project root for absolute imports to work
from app.extensions import mongo

webhook = Blueprint('Webhook', __name__, url_prefix='/webhook')

@webhook.route('/receiver', methods=["POST"])
def receiver():
    if mongo.db is None:
        raise RuntimeError("Mongo DB has not been initialized")
    data =request.get_json(silent=True) # use get_json() to handle possible empty responses
    if not data:
        project_logger.warning("No event JSON received!")
        return jsonify({"error": "No JSON payload received"}), 400
    
    event = data.get("event")
    merged_at = data.get("merged_at")
    pr_action = data.get("pr_action")
    author = data.get("author")
    request_id = data.get("request_id")
    received_timestamp = data.get("timestamp")
    pr_from = data.get("from_branch")
    pr_to = data.get("to_branch")
    # compile all relevant data
    log_doc={
                "request_id": request_id,
                "author": author,
                "action": "",
                "from_branch": pr_from,
                "to_branch": pr_to,
                "timestamp": received_timestamp
            }

    # Push event
    if event == "push":
        log_doc["action"] = "PUSH"
        project_logger.info("[Push] Author: %s, UTC Timestamp: %s", author, received_timestamp)

    # Pull request event
    elif event == "pull_request":
        # check for merged request or not
        if merged_at:
            log_doc["action"] = "MERGE"
            project_logger.info(
                "[Pull Request Merged] From: %s, To: %s, author: %s, Author: %s, Merge Time:%s",
                pr_action,pr_from,pr_to,author,author,merged_at
            )
        else:
            log_doc["action"] = "PULL_REQUEST"
            project_logger.info(
                "[Pull Request] From: %s, To: %s, author: %s",
                pr_action,pr_from,pr_to,author
            )
    else:
        project_logger.warning("[WARNING] Unkwown Request at time: %s",received_timestamp)

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