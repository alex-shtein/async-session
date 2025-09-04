Для накатывания миграций, если файла alembic.ini ещё нет, нужно запустить в терминале команду:
```
alembic init migrations
```

После этого будет создана папка с миграциями и конфигурационный файл для алембика.

- B alembic.ini нужно задать адрес базы данных, в которую будем катать миграции.
```
sqlalchemy.url = postgresql://postgres:postgres@0.0.0.0:5432/postgres
```

- Дальше идём в папку с миграциями и открываем env.ру, там вносим изменения в блок, где написано
```
from myapp import mymodel -> from db.models import Base
```

- Раскоментируем строку ниже
```
target_metadata = Base.metadata
```

- Дальше вводим: ```alembic revision --autogenerate -m "runnnig migrations"```
- Далее: ```alembic upgrade heads```





Cоздаём конфиги `pre-commit-config.yaml` u `setup.cfg`
• Устанавливаем `pre-commit`;
• Пишем `pre-commit install`;
• Далее `pre-commit run --all-files`;
• PROFIT.