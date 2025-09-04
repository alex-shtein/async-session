# api/schemas.py
import re
import uuid
from typing import Optional

from fastapi import HTTPException
from pydantic import BaseModel
from pydantic import EmailStr
from pydantic import validator

LETTER_MATCH_PATTERN = re.compile(r"^[а-яА-Яяa-zA-Z\-]+$")


class BaseSchema(BaseModel):
    """Базовый класс для всех Pydantic схем."""

    class Config:
        orm_mode = True


class UserResponse(BaseSchema):
    """Схема для ответа с данными пользователя."""

    id: uuid.UUID
    first_name: str
    last_name: str
    email: EmailStr
    is_active: bool


class UserCreateRequest(BaseSchema):
    """Схема для запроса создания пользователя."""

    first_name: str
    last_name: str
    email: EmailStr

    @validator("first_name")
    def validate_first_name(cls, value):
        if not LETTER_MATCH_PATTERN.match(value):
            raise HTTPException(
                status_code=422, detail="First name should contain only letters"
            )
        return value

    @validator("last_name")
    def validate_last_name(cls, value):
        if not LETTER_MATCH_PATTERN.match(value):
            raise HTTPException(
                status_code=422, detail="Last name should contain only letters"
            )
        return value


class UserDeleteResponse(BaseSchema):
    """Схема для ответа при удалении пользователя."""

    id: uuid.UUID


class UserUpdateResponse(BaseSchema):
    """Схема для ответа при обновлении пользователя."""

    id: uuid.UUID


class UserUpdateRequest(BaseSchema):
    """Схема для запроса обновления пользователя."""

    first_name: Optional[str] = None
    last_name: Optional[str] = None
    email: Optional[EmailStr] = None

    @validator("first_name")
    def validate_first_name(cls, value):
        if value is not None:
            if not LETTER_MATCH_PATTERN.match(value):
                raise HTTPException(
                    status_code=422, detail="First name should contain only letters"
                )
            if len(value) < 2:
                raise HTTPException(
                    status_code=422, detail="First name must have at least 2 letters"
                )
        return value

    @validator("last_name")
    def validate_last_name(cls, value):
        if value is not None:
            if not LETTER_MATCH_PATTERN.match(value):
                raise HTTPException(
                    status_code=422, detail="Last name should contain only letters"
                )
            if len(value) < 2:
                raise HTTPException(
                    status_code=422, detail="Last name must have at least 2 letters"
                )
        return value
