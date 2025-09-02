# fetch_task.py

from flask import Blueprint, jsonify
from pymongo import MongoClient
from datetime import datetime
import os
from dotenv import load_dotenv

# ✅ Import the new function from aws_service
from app.services.aws_service import fetch_multi_groupby_cost

load_dotenv()

fetch_bp = Blueprint("fetch_bp", __name__)

MONGO_URI = os.getenv("MONGO_URI", "mongodb://localhost:27017/")
DB_NAME = os.getenv("DB_NAME", "devops_dashboard")
COLLECTION_NAME = os.getenv("COLLECTION_NAME", "aws_costs")

@fetch_bp.route("/fetch-costs", methods=["GET"])
def fetch_costs():
    """
    Fetch AWS costs with multiple groupings (SERVICE, REGION, USAGE_TYPE, OPERATION)
    and store them in MongoDB.
    """
    try:
        # ✅ Get AWS cost data
        cost_data = fetch_multi_groupby_cost()

        if not cost_data:
            return jsonify({"message": "No cost data found"}), 404

        # ✅ Save to MongoDB
        client = MongoClient(MONGO_URI)
        db = client[DB_NAME]
        collection = db[COLLECTION_NAME]

        # Optional: Add timestamp to each record
        for item in cost_data:
            item["fetched_at"] = datetime.utcnow()

        collection.insert_many(cost_data)

        return jsonify({
            "message": "AWS costs fetched and stored successfully",
            "records_inserted": len(cost_data)
        }), 200

    except Exception as e:
        return jsonify({"error": str(e)}), 500
