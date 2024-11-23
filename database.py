# database.py

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from .config import DATABASE_URL

# Example DATABASE_URL: "postgresql://fastapi_user:yourpassword@localhost/fastapi_auth"
DATABASE_URL = "postgresql://fastapi_user:yourpassword@localhost/fastapi_auth"

engine = create_engine(DATABASE_URL)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
