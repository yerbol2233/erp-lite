"""
Модель клиента.
Контрагенты, которым продаём товары/услуги.
"""

from datetime import datetime
from sqlalchemy import Column, Integer, String, DateTime, Text
from sqlalchemy.orm import relationship

from db.database import Base


class Client(Base):
    """
    Таблица клиентов (контрагентов).
    
    Клиент может иметь много заказов.
    Хранятся контактные данные и реквизиты.
    """
    __tablename__ = "clients"
    
    id = Column(Integer, primary_key=True, index=True)
    
    # Основные данные
    name = Column(String(255), nullable=False, index=True)
    company = Column(String(255), nullable=True)  # Название компании
    
    # Контакты
    phone = Column(String(50), nullable=True)
    email = Column(String(255), nullable=True)
    
    # Адрес
    city = Column(String(100), nullable=True, index=True)
    address = Column(Text, nullable=True)
    
    # Дополнительно
    inn = Column(String(20), nullable=True)  # ИНН для юрлиц
    notes = Column(Text, nullable=True)  # Заметки менеджера
    
    # Служебные поля
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Связи
    orders = relationship("Order", back_populates="client", lazy="dynamic")
    
    def __repr__(self):
        return f"<Client {self.name}>"
