from pydantic import BaseModel
from typing import Optional, Literal, Dict, Any
from datetime import datetime
from uuid import UUID

# ---------- User ----------
class User(BaseModel):
    # DB fields (server-managed) - default to None so they are not required in requests
    id: Optional[UUID] = None
    telegram_id: Optional[int] = None
    phone: Optional[str] = None
    full_name: Optional[str] = None
    email: Optional[str] = None
    consent: bool = False
    balance: float = 0.0
    # avoid mutable default values
    metadata: Optional[Dict[str, Any]] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None


# Schema for incoming create requests (only include fields clients should provide)
class UserCreate(BaseModel):
    telegram_id: Optional[int] = None
    phone: Optional[str] = None
    full_name: Optional[str] = None
    email: Optional[str] = None
    consent: Optional[bool] = False
    metadata: Optional[Dict[str, Any]] = None

# ---------- Interaction ----------
class Interaction(BaseModel):
    id: Optional[UUID] = None
    user_id: UUID
    telegram_message_id: Optional[int] = None
    direction: Literal["in", "out"] = "in"
    message_text: str
    metadata: Optional[Dict[str, Any]] = None
    created_at: Optional[datetime] = None
