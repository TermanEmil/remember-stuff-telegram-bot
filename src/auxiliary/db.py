import os

from pymongo.mongo_client import MongoClient
from pymongo.server_api import ServerApi


DB_NAME = 'bot-assistant-db'
CONVERSATIONS_NAME = 'conversations'
USER_DATA_NAME = 'user_data'
USER_CONTENT_NAME = 'user_content'


def get_db_client() -> MongoClient:
    # Create a new client and connect to the server
    uri = os.environ.get('MONGO_DB_URI')
    return MongoClient(uri, server_api=ServerApi('1'))
