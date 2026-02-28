from flask import Flask
from .extensions import init_app
from .webhook.routes import webhook

def create_app():
    app = Flask(__name__)
    init_app(app)
    app.register_blueprint(webhook)
    return app