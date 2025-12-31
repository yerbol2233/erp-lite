"""
Модель пользователя.
Хранит данные для аутентификации и роли в системе.
"""

from datetime import datetime
from sqlalchemy import Column, Integer, String, Boolean, DateTime
from sqlalchemy.orm import relationship

from db.database import Base


class User(Base):
    """
    Таблица пользователей системы.
    
    Роли:
        - admin: полный доступ ко всем функциям
        - manager: работа с заказами и клиентами
        - viewer: только просмотр данных
    """
    __tablename__ = "users"
    
    id = Column(Integer, primary_key=True, index=True)
    email = Column(String(255), unique=True, index=True, nullable=False)
    hashed_password = Column(String(255), nullable=False)
    
    # Профиль пользователя
    full_name = Column(String(255), nullable=True)
    
    # Роль и статус
    role = Column(String(50), default="viewer")  # admin, manager, viewer
    is_active = Column(Boolean, default=True)
    
    # Служебные поля
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    def __repr__(self):
        return f"<User {self.email}>"
