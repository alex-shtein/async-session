# api/handlers.py
from logging import getLogger
from typing import Optional
from uuid import UUID

from fastapi import APIRouter
from fastapi import Depends
from fastapi import HTTPException
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from api.schemas import UserCreateRequest
from api.schemas import UserDeleteResponse
from api.schemas import UserResponse
from api.schemas import UserUpdateRequest
from api.schemas import UserUpdateResponse
from db.repositories import UserRepository
from db.session import get_db
from utils.hasher import Hasher

logger = getLogger(__name__)

user_router = APIRouter()


async def _create_user(
    body: UserCreateRequest, db: AsyncSession = Depends(get_db)
) -> UserResponse:
    """Внутренняя функция для создания пользователя."""
    async with db as session:
        async with session.begin():
            repository = UserRepository(session)
            user = await repository.create(
                first_name=body.first_name,
                last_name=body.last_name,
                email=body.email,
                hashed_password=Hasher.get_password_hash(body.password),
            )

            return UserResponse(
                id=user.id,
                first_name=user.first_name,
                last_name=user.last_name,
                email=user.email,
                is_active=user.is_active,
            )


async def _get_user(user_id: UUID, db) -> Optional[UserResponse]:
    """Внутренняя функция для получения пользователя."""
    async with db as session:
        async with session.begin():
            repository = UserRepository(session)
            user = await repository.get_by_id(user_id=user_id)
            if user:
                return UserResponse(
                    id=user.id,
                    first_name=user.first_name,
                    last_name=user.last_name,
                    email=user.email,
                    is_active=user.is_active,
                )
    return None


async def _delete_user(user_id: UUID, db) -> Optional[UUID]:
    """Внутренняя функция для удаления пользователя."""
    async with db as session:
        async with session.begin():
            repository = UserRepository(session)
            return await repository.delete(user_id=user_id)


async def _update_user(user_id: UUID, update_data: dict, db) -> Optional[UUID]:
    """Внутренняя функция для обновления пользователя."""
    async with db as session:
        async with session.begin():
            repository = UserRepository(session)
            return await repository.update(user_id, **update_data)


@user_router.post("/", response_model=UserResponse)
async def create_user(
    body: UserCreateRequest, db: AsyncSession = Depends(get_db)
) -> UserResponse:
    """Создает нового пользователя."""
    try:
        return await _create_user(body, db)
    except IntegrityError as err:
        logger.error(err)
        raise HTTPException(status_code=503, detail=f"Database error: {err}")


@user_router.delete("/", response_model=UserDeleteResponse)
async def delete_user(
    user_id: UUID, db: AsyncSession = Depends(get_db)
) -> UserDeleteResponse:
    """Удаляет пользователя."""
    deleted_user_id = await _delete_user(user_id, db)
    if not deleted_user_id:
        raise HTTPException(
            status_code=404, detail=f"User with id {user_id} not found."
        )
    return UserDeleteResponse(id=deleted_user_id)


@user_router.get("/", response_model=UserResponse)
async def get_user(user_id: UUID, db: AsyncSession = Depends(get_db)) -> UserResponse:
    """Получает пользователя по ID."""
    user = await _get_user(user_id, db)
    if not user:
        raise HTTPException(
            status_code=404, detail=f"User with id {user_id} not found."
        )
    return user


@user_router.patch("/", response_model=UserUpdateResponse)
async def update_user(
    user_id: UUID, body: UserUpdateRequest, db: AsyncSession = Depends(get_db)
) -> UserUpdateResponse:
    """Обновляет данные пользователя."""
    update_data = body.dict(exclude_none=True)
    if not update_data:
        raise HTTPException(
            status_code=422,
            detail="At least one parameter for user update should be provided",
        )

    user = await _get_user(user_id, db)
    if not user:
        raise HTTPException(
            status_code=404, detail=f"User with id {user_id} not found."
        )

    try:
        updated_user_id = await _update_user(
            update_data=update_data, db=db, user_id=user_id
        )
    except IntegrityError as err:
        logger.error(err)
        raise HTTPException(status_code=503, detail=f"Database error: {err}")

    return UserUpdateResponse(id=updated_user_id)
