from datetime import timedelta
from typing import Optional

from fastapi import APIRouter
from fastapi import Depends
from fastapi import HTTPException
from fastapi import status
from fastapi.security import OAuth2PasswordBearer
from fastapi.security import OAuth2PasswordRequestForm
from jose import jwt
from jose import JWTError
from api.schemas import Token
from sqlalchemy.ext.asyncio import AsyncSession

from db.models import User
from db.repositories import UserRepository
from db.session import get_db
from utils import settings
from utils.hasher import Hasher
from utils.security import create_access_token

login_router = APIRouter()


async def get_user_by_email(email: str, db_session: AsyncSession) -> Optional[User]:
    async with db_session as session:
        async with session.begin():
            user_repository = UserRepository(session)
            return await user_repository.get_by_email(email=email)


async def authenticate_user(
    email: str, password: str, db_session: AsyncSession
) -> Optional[User]:
    user = await get_user_by_email(email=email, db_session=db_session)
    if user is None:
        return None
    if not Hasher.verify_password(password, user.hashed_password):
        return None
    return user


@login_router.post("/token", response_model=Token)
async def login_for_access_token(
    form_data: OAuth2PasswordRequestForm = Depends(),
    db_session: AsyncSession = Depends(get_db),
):
    user = await authenticate_user(form_data.username, form_data.password, db_session)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )

    access_token_expiration = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": user.email, "other_custom_data": [1, 2, 3, 4]},
        expires_delta=access_token_expiration,
    )

    return {"access_token": access_token, "token_type": "bearer"}


oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/login/token")


async def get_current_user_from_token(
    token: str = Depends(oauth2_scheme), db_session: AsyncSession = Depends(get_db)
):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
    )
    try:
        payload = jwt.decode(
            token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM]
        )
        email: str = payload.get("sub")
        print("Extracted email: ", email)
        if email is None:
            raise credentials_exception
    except JWTError:
        raise credentials_exception
    user = await get_user_by_email(email=email, db_session=db_session)
    if user is None:
        raise credentials_exception
    return user


@login_router.get("/test_auth_endpoint")
async def sample_endpoint_under_jwt(
    current_user: User = Depends(get_current_user_from_token),
):
    return {"Success": True, "current_user": current_user}
