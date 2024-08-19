import creds
from urllib.parse import quote_plus
from pymongo.mongo_client import MongoClient
from pymongo.server_api import ServerApi
from pymongo import errors
import random
from schema import serialise_2
from fastapi import HTTPException

uri = f"mongodb+srv://{quote_plus(creds.Creds.USER)}:{quote_plus(creds.Creds.PASS)}@cluster0.4cy2ale.mongodb.net/?retryWrites=true&w=majority&appName=Cluster0"
client = MongoClient(uri, server_api=ServerApi('1'))

db_1 = 'users'
db_2 = 'sentence_captcha'
collection_1='user_data'
collection_2 = 'sentence_w_label'

def return_a_random_document(db:str, collection:str):
    database=client[db]
    coll=database[collection]
    count = coll.count_documents({})
    if count == 0:
        raise HTTPException(status_code=404, detail="THERE ARE NO DOCUMENTS IN THE COLLECTION")
    
    random_index = random.randint(0, count-1)
    random_document_cursor = coll.find().skip(random_index).limit(1)
    random_document=list(random_document_cursor)[0]
    serealized = serialise_2(random_document)
    if len(serealized['sentence'])>175:
        return return_a_random_document(db, collection)
    return random_document

