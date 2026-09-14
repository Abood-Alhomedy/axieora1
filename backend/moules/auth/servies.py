from datetime import datetime, timezone,timedelta
from typing  import Optional 
from django.conf.locale import da
import jwt
from passlib.context import CryptContext
# from moules.auth.schma   import TokenData
from pathlib import Path
pwd_context=CryptContext(schemes=["bcrypt"],deprecated="auto")
BASE_DIR=Path(__file__).resolve().parent

with open(BASE_DIR/"privat.pem","r") as f:
    Private_Key=f.read()


with open(BASE_DIR/"public.pem","r") as f:
    PUBLIC_KEY=f.read()    


ALGORITHEM="RS256"  
ACCESS_TOKEN_EXPIER_MINUTES=60


def hash_password(password:str)->str:
    return pwd_context.hash(password)




def verify_password(plainpassword:str,hashedpassword:str)->bool:
    return pwd_context.verify(plainpassword,hashedpassword)


def create_acces_token(data:dict, expire_delta:Optional[timedelta]=None)->str:
    to_encode=data.copy()
    if expire_delta:
        expire=datetime.now(timezone.utc)+expire_delta
    else:
          expire=datetime.now(timezone.utc)+  timedelta(minutes=ACCESS_TOKEN_EXPIER_MINUTES)



    to_encode.update({"exp":expire})
    encode_jwt=jwt.encode(to_encode,Private_Key,algorithm=ALGORITHEM)
    return encode_jwt

