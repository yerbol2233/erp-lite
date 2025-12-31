"""
Модуль models — все модели данных SQLAlchemy.
Импортируем сюда все модели для удобства.
"""

from .user import User
from .client import Client
from .product import Product
from .order import Order, OrderItem
from .payment import Payment

# Экспортируем все модели
__all__ = [
    "User",
    "Client", 
    "Product",
    "Order",
    "OrderItem",
    "Payment",
]
