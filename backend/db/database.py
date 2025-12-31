"""
Модуль работы с базой данных.
Настройка подключения SQLAlchemy и управление сессиями.
"""

from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

from core.config import get_settings

settings = get_settings()

# Для SQLite нужны специальные настройки
# check_same_thread=False разрешает использование в FastAPI
connect_args = {}
if settings.database_url.startswith("sqlite"):
    connect_args = {"check_same_thread": False}

# Создаём движок SQLAlchemy
engine = create_engine(
    settings.database_url,
    connect_args=connect_args,
    echo=settings.debug  # Логируем SQL-запросы в debug-режиме
)

# Фабрика сессий — каждый запрос получает свою сессию
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Базовый класс для всех моделей
Base = declarative_base()


def get_db():
    """
    Генератор сессии базы данных для FastAPI Depends.
    Гарантирует закрытие сессии после обработки запроса.
    
    Использование:
        @app.get("/items")
        def get_items(db: Session = Depends(get_db)):
            return db.query(Item).all()
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def init_db():
    """
    Инициализация базы данных.
    Создаёт все таблицы, если их ещё нет.
    Вызывается при старте приложения.
    """
    # Импортируем модели, чтобы SQLAlchemy знал о них
    import models  # noqa: F401
    
    # Создаём таблицы
    Base.metadata.create_all(bind=engine)
