# app/__init__.py

from flask import Flask
from dotenv import load_dotenv
from pymongo import MongoClient
import os

load_dotenv()

def create_app():
    app = Flask(__name__)

    # Load MongoDB URI from .env
    mongo_uri = os.getenv("MONGO_URI", "mongodb://localhost:27017/devops-dashboard")

    try:
        mongo_client = MongoClient(mongo_uri)
        
        # Try to extract DB name from URI
        try:
            db = mongo_client.get_default_database()
            if db is None:
                raise Exception("No default DB in URI")
        except:
            db = mongo_client["devops-dashboard"]

        app.db = db
        print("[MongoDB] Connected successfully.")
    except Exception as e:
        print(f"[MongoDB Error] {e}")
        raise

    # Register routes
    from .routes import register_routes
    register_routes(app)

    return app


