from fastapi import APIRouter, HTTPException, Form, Depends
from models import User, Token, UserInDB
from auth_functions import get_password_hash, authenticate_user, create_access_token, get_current_active_user
from database import client, db_1,collection_1, return_a_random_document, db_2, collection_2, return_the_labels, collection_3
from fastapi.security import OAuth2PasswordRequestForm
from datetime import datetime, timedelta
import creds
from schema import serialise_2
import base64
from text_to_img import get_random_image

router = APIRouter()

@router.get("/")
async def home_endpoint():
    return {'message':'hey there!'}

@router.post('/user/signup')
async def create_new_user(user: User):
    user_dict = dict(user)
    db=client[db_1]
    coll=db[collection_1]
    if coll.find_one({"username": user_dict["username"]}):
        raise HTTPException(status_code=400, detail="Username already registered")
    user_dict["hashed_password"] = get_password_hash(user_dict.pop("password"))     #since password is part of the user model it is in the response body when this function gets run it adds a field as hashed_password to the user dict and removes the orignal password field.
    try:
        coll.insert_one(user_dict)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"COULD NOT INSERT THE NEW USER = {e}")
    
@router.post('/user/signin')
async def check_the_signin(username:str, password:str):
    try:
        user= authenticate_user(db_1,collection_1, username, password)
    except Exception as e:
        raise HTTPException(status_code=401, detail=f"COULD NOT AUTHERNTICATE THE USER = {e}")
    return user

@router.post('/token', response_model=Token)
async def login_for_access_token(form_data:OAuth2PasswordRequestForm=Depends()):
    user = authenticate_user(db_1, collection_1, form_data.username, form_data.password)
    if not user:
        raise HTTPException(status_code=401, detail='INCORRECT USERNAME OR PASSWORD', headers={'WWW-Authenticate':"Bearer"})
    access_token_expires = timedelta(minutes=creds.Creds.ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={'sub':user.username},
        expires_delta=access_token_expires
    )
    return {'access_token':access_token, 'token_type':'bearer'}

@router.post('/request_captcha')
async def request_captcha(current_user:UserInDB = Depends(get_current_active_user)):
    try:
        random_document=return_a_random_document(db_2, collection_2)
    except Exception as e:
        raise HTTPException(status_code=404, detail=f"COULD NOT FETCHA A DOCUMENT LIST FROM THE COLLECTION = {e}")
    doc= serialise_2(random_document)
    image_bytes = get_random_image(
                "./BPtypewriteStrikethrough.ttf",
                doc['sentence']
            )
    image_base64 = base64.b64encode(image_bytes).decode('utf-8')
    doc['image']=image_base64
    return doc

@router.get('/request_labels')
async def request_labels(current_user:UserInDB = Depends(get_current_active_user)):
    try:
        labels=return_the_labels(db_2, collection_3)
    except Exception as e:
        raise HTTPException(status_code=404, detail=f"COULD NOT FETCH THE LABELS = {e}")
    
    return labels