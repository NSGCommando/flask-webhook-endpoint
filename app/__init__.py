from flask import Flask
from flask_cors import CORS
from app.extensions import init_my_app
from app.webhook.routes import webhook

def create_app():
    app = Flask(__name__)
    CORS(app)
    init_my_app(app)
    app.register_blueprint(webhook)
    @app.route("/")
    def index():
        return "<h1>Hello, Flask + Cloudflared!</h1>"
    return app