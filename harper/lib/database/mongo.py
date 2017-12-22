# External imports
from pymongo import MongoClient
from bson import ObjectId

# Project imports
from harper.settings import secrets

config = secrets.MONGODB_CONFIG

client = MongoClient(config["DATABASE_URI"])
db = client[config["DATABASE_NAME"]]
