"""
ERP-Lite — Система автоматизации бизнеса.

Точка входа FastAPI приложения.
Здесь подключаем все роутеры, настраиваем CORS и инициализируем БД.
"""

from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from core.config import get_settings
from db.database import init_db
from api import (
    auth_router,
    clients_router,
    products_router,
    orders_router,
    payments_router,
    reports_router,
)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    События жизненного цикла приложения.
    При старте инициализируем БД, при остановке — ничего особенного.
    """
    # Startup: создаём таблицы, если их нет
    init_db()
    yield
    # Shutdown: тут можно закрыть соединения


# Получаем настройки
settings = get_settings()

# Создаём приложение FastAPI
app = FastAPI(
    title=settings.app_name,
    version=settings.app_version,
    description="""
    ## ERP-Lite — Система автоматизации бизнеса
    
    Программный продукт для автоматизации учёта заказов, 
    финансовых операций и анализа бизнес-показателей.
    
    ### Возможности:
    - 📋 Управление заказами и позициями
    - 👥 База клиентов (контрагентов)
    - 📦 Номенклатура товаров
    - 💰 Учёт платежей и задолженностей
    - 📊 Аналитические отчёты
    """,
    lifespan=lifespan,
    docs_url="/docs",  # Swagger UI
    redoc_url="/redoc",  # ReDoc
)

# Настраиваем CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
)


# Подключаем роутеры API
app.include_router(auth_router, prefix="/api")
app.include_router(clients_router, prefix="/api")
app.include_router(products_router, prefix="/api")
app.include_router(orders_router, prefix="/api")
app.include_router(payments_router, prefix="/api")
app.include_router(reports_router, prefix="/api")


@app.get("/", tags=["Система"])
def root():
    """Корневой эндпоинт — проверка работоспособности."""
    return {
        "service": settings.app_name,
        "version": settings.app_version,
        "status": "running",
        "docs": "/docs"
    }


@app.get("/health", tags=["Система"])
def health_check():
    """Проверка здоровья сервиса для мониторинга."""
    return {"status": "healthy"}


# Для запуска напрямую через python main.py
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=settings.debug
    )
