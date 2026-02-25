from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List, Optional
from app import schemas
from app.services import request_service
from app.dependencies import get_db, get_current_user
from app.models import User, RequestStatus

router = APIRouter(prefix="/requests", tags=["requests"])

@router.get("/", response_model=List[schemas.RequestOut])
async def get_requests(
    status: Optional[RequestStatus] = Query(None),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    if current_user.role == "dispatcher":
        requests = await request_service.get_all_requests(db, status)
    else:
        requests = await request_service.get_my_requests(db, current_user.id, status)
    return requests

@router.patch("/{request_id}/assign", response_model=schemas.RequestOut)
async def assign_master(
    request_id: int,
    master_id: int = Query(...),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    if current_user.role != "dispatcher":
        raise HTTPException(403, "Only dispatcher can assign master")
    req = await request_service.assign_master(db, request_id, master_id)
    if not req:
        raise HTTPException(404, "Request not found or cannot be assigned")
    return req

@router.patch("/{request_id}/cancel", response_model=schemas.RequestOut)
async def cancel_request(
    request_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    if current_user.role != "dispatcher":
        raise HTTPException(403, "Only dispatcher can cancel requests")
    req = await request_service.cancel_request(db, request_id)
    if not req:
        raise HTTPException(404, "Request not found or cannot be canceled")
    return req

@router.patch("/{request_id}/take", response_model=schemas.RequestOut)
async def take_request(
    request_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    if current_user.role != "master":
        raise HTTPException(403, "Only master can take request")
    req = await request_service.take_request(db, request_id, current_user.id)
    if not req:
        raise HTTPException(409, detail="Request already taken or status changed")
    return req

@router.patch("/{request_id}/complete", response_model=schemas.RequestOut)
async def complete_request(
    request_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    if current_user.role != "master":
        raise HTTPException(403, "Only master can complete request")
    req = await request_service.complete_request(db, request_id, current_user.id)
    if not req:
        raise HTTPException(404, "Request not found or cannot be completed")
    return req
@router.post("/", response_model=schemas.RequestOut, status_code=201)
async def create_request(
    request_data: schemas.RequestCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    # Только диспетчер может создавать заявки (можно убрать проверку, если нужно всем)
    if current_user.role != "dispatcher":
        raise HTTPException(403, "Only dispatcher can create requests")
    req = await request_service.create_request(db, request_data)
    return req