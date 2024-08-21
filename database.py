import creds
from urllib.parse import quote_plus
from pymongo.mongo_client import MongoClient
from pymongo.server_api import ServerApi
from pymongo import errors
import random
from schema import serialise_2, serealise_3
from fastapi import HTTPException
from models import RequestedData
import smtplib
from bson import ObjectId
from datetime import datetime

uri = f"mongodb+srv://{quote_plus(creds.Creds.USER)}:{quote_plus(creds.Creds.PASS)}@cluster0.4cy2ale.mongodb.net/?retryWrites=true&w=majority&appName=Cluster0"
client = MongoClient(uri, server_api=ServerApi('1'))
s = smtplib.SMTP("smtp.gmail.com", 587)

db_1 = 'users'
db_2 = 'sentence_captcha'
collection_1='user_data'
collection_2 = 'sentence_w_label'
collection_3='label_classes'
collection_4='user_request_data'
collection_5='vericaptcha_output'


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
    if len(serealized['sentence'])>35:
        return return_a_random_document(db, collection)
    return random_document

def return_the_labels(db:str, collection:str):
    database=client[db]
    coll=database[collection]
    count= coll.count_documents({})
    if count == 0:
        raise HTTPException(status_code=404, detail="THERE ARE NO DOCUMENTS IN THE COLLECTION")
    labels={}
    cursor=coll.find()
    cursor_list=list(cursor)
    for c in cursor_list:
        serealized = serealise_3(c)
        labels[serealized['label']]=serealized['label_class']
    return labels


def send_email(data: RequestedData):
    s.connect("smtp.gmail.com", 587)
    s.starttls()
    s.login("vericaptcha@gmail.com", "kztc ebqp imkk jyll")
    subject = "Custom Dataset Request Received"
    body = f"""
    Hey {data['name']},

    We hope this message finds you well.

    We are pleased to inform you that we have received your custom dataset request. Our team will review the details and get back to you shortly to discuss further specifics.

    Thank you for choosing VeriCaptcha. We look forward to assisting you with your data needs.

    Best regards,
    The VeriCaptcha Team
    """
    message = f"Subject: {subject}\n\n{body}"
    s.sendmail("vericaptcha@gmail.com", data["email"], message)
    s.quit()

def add_requested_data(data: RequestedData):
    try:
        database=client[db_2]
        coll = database[collection_4]
        coll.insert_one(data)
    except errors.PyMongoError as e:
        raise Exception(f'{e}')


def find_update_and_upsert(db:str, collection:str, id:str, suspected_label:str):
    try:
        database=client[db]
        coll=database[collection]
    except Exception as e:
        raise HTTPException(status_code=500, detail=f'there is no collection by the name {collection} = {e}')
    
    current_time = datetime.now().strftime('%Y%m%d%H%M%S')
    dynamic_key = f'suspected_label_{current_time}'

    try:
        coll.find_one_and_update(
            {'_id':ObjectId(id)},
            {'$set':{'_id':ObjectId(id), dynamic_key:suspected_label}},
            upsert=True
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=e)

def update_the_score(username:str, current_score:int):
    database=client[db_1]
    coll=database[collection_1]
    try:
        coll.find_one_and_update(
            {'username':username},
            {'$set':{'score':current_score+1}}
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=e)
