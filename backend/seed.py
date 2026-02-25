import asyncio
from app.core.database import async_session
from app.models import User, Request, UserRole, RequestStatus

async def seed():
    async with async_session() as db:
        # Проверим, есть ли уже пользователи
        from sqlalchemy import select
        result = await db.execute(select(User))
        if result.scalars().first():
            print("Database already seeded")
            return

        # Пользователи
        dispatcher = User(name="dispatcher", role=UserRole.dispatcher)
        master1 = User(name="master1", role=UserRole.master)
        master2 = User(name="master2", role=UserRole.master)
        db.add_all([dispatcher, master1, master2])
        await db.commit()

        # Заявки
        requests = [
            Request(clientName="Иван Петров", phone="+79001234567", address="ул. Ленина 1", problemText="Не включается", status=RequestStatus.new),
            Request(clientName="Мария Сидорова", phone="+79007654321", address="ул. Гагарина 5", problemText="Шумит", status=RequestStatus.assigned, assignedTo=master1.id),
            Request(clientName="Петр Иванов", phone="+79001112233", address="пр. Мира 10", problemText="Течёт", status=RequestStatus.in_progress, assignedTo=master2.id),
            Request(clientName="Ольга Смирнова", phone="+79005556677", address="ул. Лесная 3", problemText="Не греет", status=RequestStatus.done, assignedTo=master1.id),
            Request(clientName="Алексей Козлов", phone="+79008889900", address="пер. Садовый 7", problemText="Стучит", status=RequestStatus.canceled),
        ]
        db.add_all(requests)
        await db.commit()
        print("Seed completed")

if __name__ == "__main__":
    asyncio.run(seed())