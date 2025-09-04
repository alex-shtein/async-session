# Миграции с Alembic

## Установка и настройка

1. Установите Alembic:
```bash
pip install alembic
```

2. Инициализируйте миграции (если файл `alembic.ini` еще не создан):
```bash
alembic init migrations
```

## Конфигурация

1. Настройте подключение к базе данных в `alembic.ini`:
```ini
sqlalchemy.url = postgresql://postgres:postgres@0.0.0.0:5432/postgres
```

2. В файле `migrations/env.py` внесите изменения:
```python
# Замените импорт
from myapp import mymodel  # Было
from db.models import Base  # Стало

# Раскомментируйте строку
target_metadata = Base.metadata
```

## Создание и применение миграций

1. Создайте автоматическую миграцию:
```bash
alembic revision --autogenerate -m "running migrations"
```

2. Примените миграции:
```bash
alembic upgrade heads
```

## Настройка pre-commit

1. Установите pre-commit:
```bash
pip install pre-commit
```

2. Создайте файл `.pre-commit-config.yaml` и `setup.cfg`

3. Установите pre-commit хуки:
```bash
pre-commit install
```

4. Запустите проверку для всех файлов:
```bash
pre-commit run --all-files
```
