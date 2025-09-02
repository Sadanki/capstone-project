from pymongo import MongoClient
import os
from dotenv import load_dotenv

load_dotenv()

MONGO_URI = os.getenv("MONGO_URI", "mongodb://localhost:27017/devops_dashboard")

client = MongoClient(MONGO_URI)
db = client.get_default_database()
cost_collection = db["aws_costs"]