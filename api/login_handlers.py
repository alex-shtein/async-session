from datetime import timedelta
from typing import Optional

from fastapi import APIRouter
from fastapi import Depends
from fastapi import HTTPException
from fastapi import status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.ext.asyncio import AsyncSession

from api.schemas import Token
from db.models import User
from db.repositories import UserRepository
from db.session import get_db
from utils import settings
from utils.hasher import Hasher
from utils.security import create_access_token

login_router = APIRouter()


async def _fetch_user_by_email(email: str, db: AsyncSession) -> Optional[User]:
    async with db as session:
        async with session.begin():
            repo = UserRepository(session)
            return await repo.get_by_email(email=email)


async def authenticate_user(
    email: str, password: str, db: AsyncSession
) -> Optional[User]:
    user = await _fetch_user_by_email(email=email, db=db)
    if user is None:
        return None
    if not Hasher.verify_password(password, user.hashed_password):
        return None
    return user


@login_router.post("/token", response_model=Token)
async def login_for_access_token(
    form_data: OAuth2PasswordRequestForm = Depends(),
    db: AsyncSession = Depends(get_db),
):
    user = await authenticate_user(form_data.username, form_data.password, db)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )

    access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": user.email, "other_custom_data": [1, 2, 3, 41]},
        expires_delta=access_token_expires,
    )

    return {"access_token": access_token, "token_type": "bearer"}
