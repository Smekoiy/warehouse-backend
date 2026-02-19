from pydantic import BaseModel
from typing import Optional


class UserCreate(BaseModel):
    username: str
    full_name: str
    password: str
    role: str


class ItemCreate(BaseModel):
    code: str
    name: str
    description: Optional[str] = None


class MovementCreate(BaseModel):
    item_id: int
    quantity: float
