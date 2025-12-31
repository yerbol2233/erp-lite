"""
Модуль schemas — все Pydantic-схемы для валидации.
"""

from .user import (
    UserCreate, UserUpdate, UserRead,
    Token, TokenData, LoginRequest
)
from .client import ClientCreate, ClientUpdate, ClientRead, ClientList
from .product import ProductCreate, ProductUpdate, ProductRead, ProductList
from .order import (
    OrderCreate, OrderUpdate, OrderRead, OrderList,
    OrderItemCreate, OrderItemRead
)
from .payment import PaymentCreate, PaymentUpdate, PaymentRead, PaymentList

__all__ = [
    # Пользователи
    "UserCreate", "UserUpdate", "UserRead",
    "Token", "TokenData", "LoginRequest",
    # Клиенты
    "ClientCreate", "ClientUpdate", "ClientRead", "ClientList",
    # Товары
    "ProductCreate", "ProductUpdate", "ProductRead", "ProductList",
    # Заказы
    "OrderCreate", "OrderUpdate", "OrderRead", "OrderList",
    "OrderItemCreate", "OrderItemRead",
    # Платежи
    "PaymentCreate", "PaymentUpdate", "PaymentRead", "PaymentList",
]
