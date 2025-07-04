from pymongo import MongoClient
import os

client = MongoClient(os.environ.get("MONGO_URI"))
db = client["webhookDB"]
events = db["events"]