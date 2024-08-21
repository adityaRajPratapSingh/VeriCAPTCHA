from fastapi import APIRouter, HTTPException, Form, Depends
from models import User, Token, UserInDB, RequestedData, CaptchaResponse, signin
from auth_functions import get_password_hash, authenticate_user, create_access_token, get_current_active_user
from database import client, db_1,collection_1, return_a_random_document, db_2, collection_2, return_the_labels, collection_3, add_requested_data, send_email, find_update_and_upsert, collection_5, update_the_score
from fastapi.security import OAuth2PasswordRequestForm
from datetime import datetime, timedelta
import creds
from schema import serialise_2
import base64
from text_to_img import get_random_image
from pydantic import EmailStr
from text_to_image_new import the_image
from text_to_image_new_labels import the_image_labels

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
async def check_the_signin(signin_user:signin):
    try:
        user= authenticate_user(db_1,collection_1, signin_user.username, signin_user.password)
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

@router.post('/captcha/request_captcha')
async def request_captcha(current_user:UserInDB = Depends(get_current_active_user)):
    try:
        random_document=return_a_random_document(db_2, collection_2)
    except Exception as e:
        raise HTTPException(status_code=404, detail=f"COULD NOT FETCHA A DOCUMENT LIST FROM THE COLLECTION = {e}")
    doc= serialise_2(random_document)
    image_bytes = the_image( doc['sentence'])
    image_base64 = base64.b64encode(image_bytes).decode('utf-8')
    doc['image']=image_base64
    return doc

@router.get('/captcha/request_labels')
async def request_labels(current_user:UserInDB = Depends(get_current_active_user)):
    d={}
    try:
        labels=return_the_labels(db_2, collection_3)
    except Exception as e:
        raise HTTPException(status_code=404, detail=f"COULD NOT FETCH THE LABELS = {e}")
    for i in  labels.values():
        image_bytes=the_image_labels(i)
        image_base64=base64.b64encode(image_bytes).decode('utf-8')
        d[i]=image_base64
    return d

@router.post("/submit_request")
async def submit_request(
        name: str = Form(...),
        address: str = Form(...),
        email: EmailStr = Form(...),
        phone: str = Form(...),
        request_detail: str = Form(...),
):
    data = {
        "name": name,
        "address": address,
        "email": email,
        "phone": phone,
        "description": request_detail,
    }
    add_requested_data(data)
    send_email(data)
    return {"message": "order successfully received"}

@router.post('/captcha/captcha_response')
async def captcha_response(response:CaptchaResponse, current_user:UserInDB = Depends(get_current_active_user)):
    try:
        labels=return_the_labels(db_2, collection_3)
    except Exception as e:
        raise HTTPException(status_code=404, detail=f"COULD NOT FETCH THE LABELS = {e}")
    if response.suspected_label not in labels.values():
        return False
    else:
        find_update_and_upsert(db_2, collection_5, response.id, response.suspected_label)
        update_the_score(current_user.username, current_user.score)
        return True