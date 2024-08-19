import creds
from urllib.parse import quote_plus
from pymongo.mongo_client import MongoClient
from pymongo.server_api import ServerApi
from pymongo import errors

uri = f"mongodb+srv://{quote_plus(creds.Creds.USER)}:{quote_plus(creds.Creds.PASS)}@cluster0.4cy2ale.mongodb.net/?retryWrites=true&w=majority&appName=Cluster0"
client = MongoClient(uri, server_api=ServerApi('1'))

db_1 = 'users'
collection_1='user_data'