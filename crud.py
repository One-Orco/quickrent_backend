from datetime import datetime, timedelta
from typing import Optional
from jose import JWTError, jwt
from passlib.context import CryptContext  # Missing import added here
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
import models, crud
from database import get_db
from sqlalchemy.orm import Session
from sqlalchemy import func
import models, schemas
from auth import get_password_hash

SECRET_KEY = "hitestyounes"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")


def get_user_by_username(db: Session, username: str):
    return db.query(models.User).filter(models.User.username == username).first()

def get_user_by_email(db: Session, email: str):
    return db.query(models.User).filter(models.User.email == email).first()

def create_user(db: Session, user: schemas.UserCreate):
    hashed_password = get_password_hash(user.password)
    db_user = models.User(
        username=user.username,
        email=user.email,
        hashed_password=hashed_password,
        role=user.role,
    )
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user

def verify_password(plain_password, hashed_password):
    return pwd_context.verify(plain_password, hashed_password)

def get_password_hash(password):
    return pwd_context.hash(password)

def create_access_token(data: dict, expires_delta: Optional[timedelta] = None):
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=15)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

def get_current_user(
    token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)
):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get("sub")
        if username is None:
            raise credentials_exception
    except JWTError:
        raise credentials_exception
    user = crud.get_user_by_username(db, username=username)
    if user is None:
        raise credentials_exception
    return user

def get_current_active_user(
    current_user: models.User = Depends(get_current_user),
):
    return current_user


def get_deals(db: Session, skip: int = 0, limit: int = 100):
    return db.query(models.Deal).offset(skip).limit(limit).all()

def create_deal(db: Session, deal: schemas.DealCreate, agent_id: int):
    db_deal = models.Deal(
        **deal.dict(),
        agent_id=agent_id,
        status="pending",
    )
    db.add(db_deal)
    db.commit()
    db.refresh(db_deal)
    return db_deal

def get_deals_by_agent(db: Session, agent_id: int, skip: int = 0, limit: int = 100):
    return (
        db.query(models.Deal)
        .filter(models.Deal.agent_id == agent_id)
        .offset(skip)
        .limit(limit)
        .all()
    )
def update_deal_status(db: Session, deal_id: int, status: str):
    deal = db.query(models.Deal).filter(models.Deal.id == deal_id).first()
    if not deal:
        return None
    deal.status = status
    db.commit()
    db.refresh(deal)
    return deal


def get_total_deals_by_status(db: Session):
    results = db.query(models.Deal.status, func.count(models.Deal.id)).group_by(models.Deal.status).all()
    return [{"status": result[0], "count": result[1]} for result in results]

def get_top_performing_agents(db: Session, limit: int = 5):
    results = (
        db.query(models.User.username, func.count(models.Deal.id))
        .join(models.Deal, models.User.id == models.Deal.agent_id)
        .filter(models.Deal.status == "approved")
        .group_by(models.User.username)
        .order_by(func.count(models.Deal.id).desc())
        .limit(limit)
        .all()
    )
    return [{"username": result[0], "approved_deals": result[1]} for result in results]

def get_most_popular_property_types(db: Session):
    results = db.query(models.Deal.property_type, func.count(models.Deal.id)).group_by(models.Deal.property_type).all()
    return [{"property_type": result[0], "count": result[1]} for result in results]

def get_deals_by_location(db: Session):
    results = db.query(models.Deal.location, func.count(models.Deal.id)).group_by(models.Deal.location).all()
    return [{"location": result[0], "count": result[1]} for result in results]

def get_total_earnings(db: Session):
    total_earnings = db.query(func.sum(models.Deal.price)).filter(models.Deal.status == "approved").scalar()
    return {"total_earnings": total_earnings or 0}
