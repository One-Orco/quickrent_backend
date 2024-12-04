from pydantic import BaseModel, Field
from typing import Optional
import datetime

class UserBase(BaseModel):
    username: str
    email: str

class UserCreate(UserBase):
    password: str
    role: str

class User(UserBase):
    id: int
    role: str


class DealBase(BaseModel):
    property_type: str = Field(..., description="Type of the property (e.g., apartment, villa)")
    transaction_type: str = Field(..., description="Transaction type (rent, buy, sell)")
    location: str = Field(..., description="Location of the property (e.g., Dubai Marina)")
    size: float = Field(..., gt=0, description="Size of the property in square meters")
    bedrooms: Optional[int] = Field(None, ge=0, description="Number of bedrooms")
    bathrooms: Optional[int] = Field(None, ge=0, description="Number of bathrooms")
    price: float = Field(..., gt=0, description="Price in AED")
    currency: str = Field(default="AED", description="Currency of the price")
    buyer_info: str = Field(..., description="Details about the buyer")
    landlord_info: str = Field(..., description="Details about the landlord")
    amenities: Optional[str] = Field(None, description="Amenities provided (e.g., pool, gym)")
    description: Optional[str] = Field(None, description="Additional description of the property")

class DealCreate(DealBase):
    pass

class Deal(DealBase):
    id: int
    agent_id: int
    status: str
    created_at: datetime.datetime
    updated_at: datetime.datetime

    class Config:
        orm_mode = True