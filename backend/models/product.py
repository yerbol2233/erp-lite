"""
Модель товара/продукта.
Номенклатура для продажи.
"""

from datetime import datetime
from decimal import Decimal
from sqlalchemy import Column, Integer, String, DateTime, Numeric, Text

from db.database import Base


class Product(Base):
    """
    Таблица товаров/услуг.
    
    Хранит номенклатуру с ценами и остатками.
    """
    __tablename__ = "products"
    
    id = Column(Integer, primary_key=True, index=True)
    
    # Основные данные
    name = Column(String(255), nullable=False, index=True)
    sku = Column(String(100), unique=True, nullable=True)  # Артикул
    
    # Цена и валюта
    price = Column(Numeric(15, 2), nullable=False, default=0)
    currency = Column(String(10), default="KZT")  # KZT, USD, RUB
    
    # Единица измерения и остаток
    unit = Column(String(50), default="шт")  # шт, кг, м, л и т.д.
    stock_quantity = Column(Numeric(15, 3), default=0)  # Текущий остаток
    
    # Категория и описание
    category = Column(String(100), nullable=True, index=True)
    description = Column(Text, nullable=True)
    
    # Статус
    is_active = Column(Integer, default=1)  # 1 = активен, 0 = архив
    
    # Служебные поля
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    def __repr__(self):
        return f"<Product {self.name} ({self.sku})>"
