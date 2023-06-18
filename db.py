import os

from pymongo.mongo_client import MongoClient
from pymongo.server_api import ServerApi


def get_db() -> MongoClient:
    # Create a new client and connect to the server
    uri = os.environ.get('MONGO_DB_URI')
    return MongoClient(uri, server_api=ServerApi('1'))
