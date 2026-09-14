from datetime import datetime, timedelta, timezone
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.orm import Session
from database.database import get_db

from moules.auth.schma import TokenResponse, UserLogin
from moules.auth.servies import verify_password, create_acces_token,ACCESS_TOKEN_EXPIER_MINUTES
from database.database import SessionLocal
from database.models import User

router = APIRouter(prefix="/api/auth", tags=["Auth"])

@router.post("/login", response_model=TokenResponse)
def login(user_credentials: UserLogin, db: Session = Depends(get_db)):
    # 1. البحث عن المستخدم بالبريد الإلكتروني (طريقة SQLAlchemy 2.0)
    user = db.execute(
        select(User).where(User.email == user_credentials.email)
    ).scalar_one_or_none()
    
    # 2. التحقق من وجود المستخدم وصحة كلمة المرور
    if not user or not verify_password(user_credentials.password,  user.password_hash):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="البريد الإلكتروني أو كلمة المرور غير صحيحة",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    # 3. حساب وقت الانتهاء المحدد للتوكين
    expires_delta = timedelta(minutes=ACCESS_TOKEN_EXPIER_MINUTES)
    expire_time = datetime.now(timezone.utc) + expires_delta

    # 4. إنشاء توكين Access Token جديد بواسطة RS256
    access_token = create_acces_token(
        data={"sub": str(user.id), "email": user.email},
         expire_delta=expires_delta
    )
    
    # 5. إرجاع النتيجة متطابقة تماماً مع TokenResponse Schema
    return {
        "access_token": access_token,
        "token_type": "bearer",
        "expires_at": expire_time
    }
