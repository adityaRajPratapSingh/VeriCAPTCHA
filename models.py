from pydantic import BaseModel, EmailStr

class Token(BaseModel):
    access_token:str
    token_type:str      #like (bearer)

class TokenData(BaseModel):     #data encoded in the access token
    username:str | None = None

class User(BaseModel):
    username:str
    password:str
    email:str | None = None
    full_name:str | None =None
    disabled:bool | None=None
    score:int = 0

class User_wop(BaseModel):  #wop = without password
    username:str
    email:str | None = None
    full_name:str | None =None
    disabled:bool | None=None
    score:int = 0

class UserInDB(User_wop):
    hashed_password:str

class RequestedData(BaseModel):
    name: str
    email: EmailStr
    requested_detail: str
    phone_no: int