from pydantic import BaseModel, EmailStr
from typing import Optional
from datetime import datetime

from uuid import UUID



class UserLogin(BaseModel):
    email: str
    password: str




class TokenResponse(BaseModel):
    access_token: str
    token_type: str ="beaerer"
    user_id:UUID
    expires_at: datetime


class TokenData(BaseModel):
    user_id: int 
    email:str
    exp:datetime





        

        