# tests/conftest.py
import os
from typing import AsyncGenerator

import asyncpg
import pytest
import pytest_asyncio
from httpx import ASGITransport
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.ext.asyncio import create_async_engine
from sqlalchemy.orm import sessionmaker

import settings
from db.session import get_db
from main import app


CLEAN_TABLES = [
    "users",
]


@pytest.fixture(scope="session", autouse=True)
def run_migrations():
    if not os.path.exists("migrations"):
        os.system("alembic init migrations")

    os.system('alembic revision --autogenerate -m "test runnnig migrations"')
    os.system("alembic upgrade heads")


@pytest_asyncio.fixture(scope="function")
async def asyncpg_pool():
    dsn = "".join(settings.TEST_DATABASE_URL.split("+asyncpg"))
    pool = await asyncpg.create_pool(dsn, min_size=1, max_size=4)
    try:
        yield pool
    finally:
        await pool.close()


@pytest_asyncio.fixture(scope="function")
async def async_session_test():
    engine_test = create_async_engine(
        settings.TEST_DATABASE_URL, future=True, echo=True
    )
    async_session_test = sessionmaker(
        engine_test, expire_on_commit=False, class_=AsyncSession
    )
    try:
        yield async_session_test
    finally:
        await engine_test.dispose()


@pytest_asyncio.fixture(scope="function", autouse=True)
async def clean_tables(asyncpg_pool):
    """Перед каждым тестом очищаем таблицы"""
    async with asyncpg_pool.acquire() as conn:
        for table in CLEAN_TABLES:
            await conn.execute(f"TRUNCATE TABLE {table} RESTART IDENTITY CASCADE;")


@pytest_asyncio.fixture(scope="function")
async def client(async_session_test) -> AsyncGenerator[AsyncClient, None]:
    async def _get_test_db():
        yield async_session_test()

    app.dependency_overrides[get_db] = _get_test_db

    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        yield ac


@pytest_asyncio.fixture
async def get_user_from_db(asyncpg_pool):
    async def get_user_from_db_by_id(user_id: str):
        async with asyncpg_pool.acquire() as connection:
            return await connection.fetchrow(
                """
                SELECT
                    *
                FROM
                    users
                WHERE
                    id = $1
                """,
                user_id,
            )

    return get_user_from_db_by_id


@pytest_asyncio.fixture
async def create_user_in_db(asyncpg_pool):
    async def create_user_in_db(
        id: str, first_name: str, last_name: str, email: str, is_active: bool
    ):
        async with asyncpg_pool.acquire() as connection:
            return await connection.fetchrow(
                """
                INSERT INTO
                    users(id, first_name, last_name, email, is_active)
                VALUES
                    ($1, $2, $3, $4, $5)
                RETURNING
                    *
                """,
                id,
                first_name,
                last_name,
                email,
                is_active,
            )

    return create_user_in_db
