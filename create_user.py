
import os

from dotenv import load_dotenv
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from backend.moules.auth.servies import hash_password
from backend.database.models import User


load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL")

if not DATABASE_URL:
    raise RuntimeError("DATABASE_URL is not set")


engine = create_engine(
    DATABASE_URL,
    pool_pre_ping=True,
)

SessionLocal = sessionmaker(
    bind=engine,
    autoflush=False,
    autocommit=False,
)


def create_user():
    db = SessionLocal()

    try:
        password = "123456"

        user = User(
            email="admin@example.com",
            password_hash=hash_password(password),
            name="Admin",
            is_active=True,
            is_verified=True,
        )

        db.add(user)
        db.commit()
        db.refresh(user)

        print("User created successfully!")
        print(f"ID: {user.id}")
        print(f"Email: {user.email}")
        print(f"Password: {password}")
        print(f"Password Hash: {user.password_hash}")

    except Exception as e:
        db.rollback()
        print(f"Error creating user: {e}")

    finally:
        db.close()


if __name__ == "__main__":
    create_user()
