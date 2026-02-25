from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from typing import List, Optional
from app import schemas
from app.models import User, UserRole
from app.dependencies import get_db, get_current_user

router = APIRouter(prefix="/users", tags=["users"])

@router.get("/", response_model=List[schemas.UserOut])
async def get_users(
    role: Optional[UserRole] = Query(None),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),  # требует аутентификации
):
    query = select(User)
    if role:
        query = query.where(User.role == role)
    result = await db.execute(query)
    return result.scalars().all()