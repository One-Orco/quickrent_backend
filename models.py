from sqlalchemy import Column, Integer, String, Enum
from sqlalchemy.ext.declarative import declarative_base
import enum

Base = declarative_base()

class UserRole(str, enum.Enum):
    agent = "agent"
    manager = "manager"
    admin = "admin"

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, index=True, nullable=False)
    hashed_password = Column(String, nullable=False)
    role = Column(Enum(UserRole), default=UserRole.agent, nullable=False)
