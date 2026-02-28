from flask_pymongo import PyMongo
import os
from dotenv import load_dotenv
load_dotenv()

mongo = PyMongo()

def init_my_app(app):
    mongo_uri = os.getenv("URI")
    if not mongo_uri:
        raise RuntimeError("URI not set in .env")
    
    app.config['MONGO_URI'] = mongo_uri
    mongo.init_app(app)
    if mongo.db is None:
        return {"error": "Database not initialized"}, 500
    # Verify connection
    with app.app_context():
        try:
            mongo.db.list_collection_names() # this will ensure the db is running
        except Exception as e: # handle the Nonetype possibility using an exception handle
            raise RuntimeError(f"Cannot connect to MongoDB: {e}")