import pytest
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession
from app.models import User, Request, UserRole, RequestStatus
from app.services.request_service import take_request

@pytest.mark.asyncio
async def test_create_request_flow(client: AsyncClient, db_session: AsyncSession):
    # Создаём диспетчера и мастера
    dispatcher = User(name="disp", role=UserRole.dispatcher)
    master = User(name="mast", role=UserRole.master)
    db_session.add_all([dispatcher, master])
    await db_session.commit()

    # Логинимся как диспетчер
    resp = await client.post("/auth/login", json={"name": "disp"})
    assert resp.status_code == 200
    cookies = resp.cookies

    # Создаём заявку (в текущем API нет создания, но можно напрямую в БД)
    req = Request(clientName="Test", phone="123", address="addr", problemText="prob", status=RequestStatus.new)
    db_session.add(req)
    await db_session.commit()
    req_id = req.id

    # Назначаем мастера
    resp = await client.patch(f"/requests/{req_id}/assign?master_id={master.id}", cookies=cookies)
    assert resp.status_code == 200
    data = resp.json()
    assert data["status"] == "assigned"
    assert data["assignedTo"] == master.id

    # Логинимся как мастер
    resp = await client.post("/auth/login", json={"name": "mast"})
    cookies = resp.cookies

    # Берём в работу
    resp = await client.patch(f"/requests/{req_id}/take", cookies=cookies)
    assert resp.status_code == 200
    data = resp.json()
    assert data["status"] == "in_progress"

    # Завершаем
    resp = await client.patch(f"/requests/{req_id}/complete", cookies=cookies)
    assert resp.status_code == 200
    data = resp.json()
    assert data["status"] == "done"

@pytest.mark.asyncio
async def test_concurrent_take(db_session: AsyncSession):
    # Создаём мастера
    master = User(name="master", role=UserRole.master)
    db_session.add(master)
    await db_session.commit()

    # Создаём заявку со статусом assigned, назначенную этому мастеру
    req = Request(clientName="Concurrent", phone="123", address="addr", problemText="prob",
                  status=RequestStatus.assigned, assignedTo=master.id)
    db_session.add(req)
    await db_session.commit()
    req_id = req.id

    # Два одновременных вызова take_request
    result1, result2 = await asyncio.gather(
        take_request(db_session, req_id, master.id),
        take_request(db_session, req_id, master.id),
        return_exceptions=True
    )

    # Один должен вернуть объект, другой None
    success_count = sum(1 for r in [result1, result2] if r is not None and not isinstance(r, Exception))
    assert success_count == 1