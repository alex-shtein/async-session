# db/repositories.py
from typing import Optional
from uuid import UUID

from sqlalchemy import and_
from sqlalchemy import select
from sqlalchemy import update
from sqlalchemy.ext.asyncio import AsyncSession

from db.models import User


class UserRepository:
    """Репозиторий для операций с пользователями в базе данных."""

    def __init__(self, db_session: AsyncSession):
        self.db_session = db_session

    async def create(
        self, first_name: str, last_name: str, email: str, hashed_password: str
    ) -> User:
        """Создает нового пользователя."""
        user = User(
            first_name=first_name,
            last_name=last_name,
            email=email,
            hashed_password=hashed_password,
        )
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

    async def get_by_email(self, email: str) -> Optional[User]:
        """Получает пользователя по ID."""
        query = select(User).where(and_(User.email == email, User.is_active == True))
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
