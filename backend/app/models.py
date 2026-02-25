from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Enum
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
import enum
from app.core.database import Base

class UserRole(str, enum.Enum):
    dispatcher = "dispatcher"
    master = "master"

class RequestStatus(str, enum.Enum):
    new = "new"
    assigned = "assigned"
    in_progress = "in_progress"
    done = "done"
    canceled = "canceled"

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, unique=True, nullable=False)
    role = Column(Enum(UserRole), nullable=False)

    assigned_requests = relationship("Request", back_populates="assigned_master", foreign_keys="Request.assignedTo")

class Request(Base):
    __tablename__ = "requests"

    id = Column(Integer, primary_key=True, index=True)
    clientName = Column(String, nullable=False)
    phone = Column(String, nullable=False)
    address = Column(String, nullable=False)
    problemText = Column(String, nullable=False)
    status = Column(Enum(RequestStatus), default=RequestStatus.new, nullable=False)
    assignedTo = Column(Integer, ForeignKey("users.id"), nullable=True)
    createdAt = Column(DateTime(timezone=True), server_default=func.now())
    updatedAt = Column(DateTime(timezone=True), onupdate=func.now(), server_default=func.now())

    assigned_master = relationship("User", back_populates="assigned_requests", foreign_keys=[assignedTo])