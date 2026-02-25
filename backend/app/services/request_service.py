from sqlalchemy import select, update
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload
from typing import List, Optional
from app.models import Request, RequestStatus
from app import schemas

async def get_all_requests(db: AsyncSession, status: Optional[RequestStatus] = None) -> List[Request]:
    query = select(Request).options(selectinload(Request.assigned_master))
    if status:
        query = query.where(Request.status == status)
    result = await db.execute(query)
    return result.scalars().all()

async def get_my_requests(db: AsyncSession, master_id: int, status: Optional[RequestStatus] = None) -> List[Request]:
    query = select(Request).where(Request.assignedTo == master_id)
    if status:
        query = query.where(Request.status == status)
    result = await db.execute(query)
    return result.scalars().all()

async def assign_master(db: AsyncSession, request_id: int, master_id: int) -> Optional[Request]:
    stmt = (
        update(Request)
        .where(Request.id == request_id, Request.status == RequestStatus.new)
        .values(assignedTo=master_id, status=RequestStatus.assigned)
        .returning(Request)
    )
    result = await db.execute(stmt)
    await db.commit()
    return result.scalar_one_or_none()

async def cancel_request(db: AsyncSession, request_id: int) -> Optional[Request]:
    stmt = (
        update(Request)
        .where(Request.id == request_id, Request.status.in_([RequestStatus.new, RequestStatus.assigned]))
        .values(status=RequestStatus.canceled)
        .returning(Request)
    )
    result = await db.execute(stmt)
    await db.commit()
    return result.scalar_one_or_none()

async def take_request(db: AsyncSession, request_id: int, master_id: int) -> Optional[Request]:
    stmt = (
        update(Request)
        .where(
            Request.id == request_id,
            Request.status == RequestStatus.assigned,
            Request.assignedTo == master_id,
        )
        .values(status=RequestStatus.in_progress)
        .returning(Request)
    )
    result = await db.execute(stmt)
    await db.commit()
    return result.scalar_one_or_none()

async def complete_request(db: AsyncSession, request_id: int, master_id: int) -> Optional[Request]:
    stmt = (
        update(Request)
        .where(
            Request.id == request_id,
            Request.status == RequestStatus.in_progress,
            Request.assignedTo == master_id,
        )
        .values(status=RequestStatus.done)
        .returning(Request)
    )
    result = await db.execute(stmt)
    await db.commit()
    return result.scalar_one_or_none()
async def create_request(db: AsyncSession, request_data: schemas.RequestCreate) -> Request:
    new_request = Request(
        clientName=request_data.clientName,
        phone=request_data.phone,
        address=request_data.address,
        problemText=request_data.problemText,
        status=RequestStatus.new
    )
    db.add(new_request)
    await db.commit()
    await db.refresh(new_request)
    return new_request