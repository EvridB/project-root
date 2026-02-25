from pydantic import BaseModel, ConfigDict
from datetime import datetime
from typing import Optional
from app.models import RequestStatus, UserRole

# User
class UserBase(BaseModel):
    name: str
    role: UserRole

class UserCreate(UserBase):
    pass

class UserOut(UserBase):
    id: int
    model_config = ConfigDict(from_attributes=True)

# Request
class RequestBase(BaseModel):
    clientName: str
    phone: str
    address: str
    problemText: str

class RequestCreate(RequestBase):
    pass

class RequestOut(RequestBase):
    id: int
    status: RequestStatus
    assignedTo: Optional[int] = None
    createdAt: datetime
    updatedAt: datetime
    model_config = ConfigDict(from_attributes=True)

# Auth
class LoginRequest(BaseModel):
    name: str