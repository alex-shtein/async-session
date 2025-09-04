# main.py
import uvicorn
from fastapi import FastAPI
from fastapi.routing import APIRouter

from api.handlers import user_router

# Создание экземпляра FastAPI приложения
app = FastAPI(title="space")

# Создание главного роутера API
main_api_router = APIRouter()

# Подключение пользовательского роутера к главному
main_api_router.include_router(user_router, prefix="/user", tags=["user"])

# Подключение главного роутера к приложению
app.include_router(main_api_router)

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
