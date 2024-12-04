from sqlalchemy import Column, Integer, String, ForeignKey, Float, DateTime
from sqlalchemy.orm import relationship
from database import Base
import datetime


class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True, index=True)
    email = Column(String, unique=True, index=True)
    hashed_password = Column(String)
    role = Column(String)
    deals = relationship("Deal", back_populates="agent")


class Deal(Base):
    __tablename__ = "deals"
    id = Column(Integer, primary_key=True, index=True)
    agent_id = Column(Integer, ForeignKey("users.id"))
    property_type = Column(String, nullable=False)  # e.g., apartment, villa
    transaction_type = Column(String, nullable=False)  # e.g., rent, buy, sell
    location = Column(String, nullable=False)  # e.g., Dubai Marina
    size = Column(Float, nullable=False)  # in square meters
    bedrooms = Column(Integer, nullable=True)  # optional for properties
    bathrooms = Column(Integer, nullable=True)  # optional for properties
    price = Column(Float, nullable=False)  # in AED
    currency = Column(String, default="AED", nullable=False)  # default to AED
    buyer_info = Column(String, nullable=False)  # buyer's name or organization
    landlord_info = Column(String, nullable=False)  # landlord's name or organization
    amenities = Column(String, nullable=True)  # e.g., pool, gym, parking
    description = Column(String, nullable=True)  # additional property details
    status = Column(String, default="pending", nullable=False)  # pending, approved, declined
    created_at = Column(DateTime, default=datetime.datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.datetime.utcnow, nullable=False)
    agent = relationship("User", back_populates="deals")
    documents = relationship("DealDocument", back_populates="deal")


class DealDocument(Base):
    __tablename__ = "deal_documents"
    id = Column(Integer, primary_key=True, index=True)
    deal_id = Column(Integer, ForeignKey("deals.id"))
    file_type = Column(String, nullable=False)  # e.g., "title_deed", "passport_copy"
    file_path = Column(String, nullable=False)  # Path to the uploaded file
    deal = relationship("Deal", back_populates="documents")



