# db/repositories.py
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import update, and_, select
from typing import Optional
from db.models import User
from uuid import UUID


class UserRepository:
    """Репозиторий для операций с пользователями в базе данных."""

    def __init__(self, db_session: AsyncSession):
        self.db_session = db_session

    async def create(self, first_name: str, last_name: str, email: str) -> User:
        """Создает нового пользователя."""
        user = User(first_name=first_name, last_name=last_name, email=email)
        self.db_session.add(user)
        await self.db_session.flush()
        return user

    async def delete(self, user_id: UUID) -> Optional[UUID]:
        """Удаляет пользователя."""
        query = (
            update(User)
            .where(and_(User.id == user_id, User.is_active == True))
            .values(is_active=False)
            .returning(User.id)
        )

        cursor = await self.db_session.execute(query)
        result = cursor.fetchone()
        return result[0] if result else None

    async def get_by_id(self, user_id: UUID) -> Optional[User]:
        """Получает пользователя по ID."""
        query = select(User).where(and_(User.id == user_id, User.is_active == True))
        cursor = await self.db_session.execute(query)
        result = cursor.fetchone()
        return result[0] if result else None

    async def update(self, user_id: UUID, **kwargs) -> Optional[UUID]:
        """Обновляет данные пользователя."""
        query = (
            update(User)
            .where(and_(User.is_active == True, User.id == user_id))
            .values(kwargs)
            .returning(User.id)
        )
        cursor = await self.db_session.execute(query)
        result = cursor.fetchone()
        return result[0] if result else None
