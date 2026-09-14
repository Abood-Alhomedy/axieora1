from pydantic import BaseModel, EmailStr
from typing import Optional
from datetime import datetime



class UserLogin(BaseModel):
    email: str
    password: str




class TokenResponse(BaseModel):
    access_token: str
    token_type: str ="beaerer"
    expires_at: datetime


class TokenData(BaseModel):
    user_id: int 
    email:str
    exp:datetime





        

        