from database import client, db_1,collection_1
from fastapi import HTTPException, Depends, status
from models import UserInDB, TokenData
from datetime import datetime, timedelta
from jose import JWTError, jwt
import creds
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from passlib.context import CryptContext
from schema import serialise_1


pwd_context=CryptContext(schemes=['bcrypt'], deprecated='auto')
oauth2_scheme=OAuth2PasswordBearer(tokenUrl='token')


#to match the plain password to the stored hashed password
def verify_password(plain_password, hashed_password):
    return pwd_context.verify(plain_password, hashed_password)
    
#return a password hash from the plain password
def get_password_hash(password:str):
    return pwd_context.hash(password)
    
#find the user with a pirticular username in the database-collection and return it
def get_user(db:str, collection:str, username:str):
    try:
        database=client[db]
        coll=database[collection]
    except Exception as e:
        raise HTTPException(status_code=500, detail=e)
    doc=coll.find_one({'username':username})
    d=serialise_1(doc)
    if d:
        d.pop('id', None)
        return UserInDB(**d)
    else:
        raise HTTPException(status_code=500, detail="the user does not exits")
        
#check of the provided username and password match after finding the username in the database-collection
def authenticate_user(db:str, collection:str, username:str, password:str):
    # user = get_user(db, collection, username)
    # if not user:
    #     return False
    # if not verify_password(password,user.hashed_password):
    #     return False
    # return user
    user= get_user(db, collection, username)
    
    if not user or not pwd_context.verify(password, user.hashed_password):
        raise HTTPException(status_code=401, detail="COULD NOT AUTHERNTICATE THE USER")

    #return UserInDB(**user)
    return user
    
#to create a new access token and encode data (a dict of username) in the access token
def create_access_token(data: dict, expires_delta: timedelta | None = None):
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=15)

    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, creds.Creds.SECRET_KEY, algorithm=creds.Creds.ALGORITHM)
    return encoded_jwt

#it retrives and verifies the current users identity based on the jtw token that it provides the web server
#and then decode it and retrieve the sub (subject) from the request.
async def get_current_user(token: str = Depends(oauth2_scheme)):
    credential_exception = HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,detail="Could not validate credentials", headers={"WWW-Authenticate": "Bearer"})
    try:
        payload = jwt.decode(token, creds.Creds.SECRET_KEY, algorithms=[creds.Creds.ALGORITHM])
        username: str = payload.get("sub")
        if username is None:
            raise credential_exception

        token_data = TokenData(username=username)
    except JWTError:
        raise credential_exception

    user = get_user(db_1, collection_1, username=token_data.username)
    if user is None:
        raise credential_exception

    return user
    
#adds another condition on the previous function that the user needs to be active the disabled users will not work
async def get_current_active_user(current_user: UserInDB = Depends(get_current_user)):
    if current_user.disabled:
        raise HTTPException(status_code=400, detail="Inactive user")

    return current_user