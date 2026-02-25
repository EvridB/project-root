from fastapi import APIRouter, Depends, HTTPException, Response
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app import schemas
from app.models import User
from app.dependencies import get_db, get_current_user

router = APIRouter(prefix="/auth", tags=["auth"])

@router.post("/login")
async def login(
    response: Response,
    login_data: schemas.LoginRequest,
    db: AsyncSession = Depends(get_db)
):
    result = await db.execute(select(User).where(User.name == login_data.name))
    user = result.scalar_one_or_none()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    response.set_cookie(key="user_id", value=str(user.id), httponly=True)
    return {"message": "Logged in", "user": schemas.UserOut.model_validate(user)}

@router.post("/logout")
async def logout(response: Response):
    response.delete_cookie("user_id")
    return {"message": "Logged out"}

@router.get("/me", response_model=schemas.UserOut)
async def get_me(user: User = Depends(get_current_user)):
    return user