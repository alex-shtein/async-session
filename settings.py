# settings.py
from envparse import Env

# Создание экземпляра Env
env = Env()

# Получение строки подключения к базе данных из переменных окружения
REAL_DATABASE_URL = env.str(
    "REAL_DATABASE_URL",
    default="postgresql+asyncpg://postgres:postgres@0.0.0.0:5432/postgres",
)

# Получение строки подключения к тестовой базе данных из переменных окружения
TEST_DATABASE_URL = env.str(
    "TEST_DATABASE_URL",
    default="postgresql+asyncpg://postgres_test:postgres_test@0.0.0.0:5433/postgres_test",
)
