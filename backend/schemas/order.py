"""
Схемы заказов для валидации.
"""

from datetime import datetime
from decimal import Decimal
from typing import Optional
from pydantic import BaseModel, Field


# --- Позиции заказа ---

class OrderItemBase(BaseModel):
    """Базовые поля позиции заказа."""
    product_id: int
    quantity: Decimal = Field(..., gt=0)
    unit_price: Decimal = Field(..., ge=0)


class OrderItemCreate(OrderItemBase):
    """Схема для добавления позиции в заказ."""
    pass


class OrderItemRead(OrderItemBase):
    """Схема для чтения позиции заказа."""
    id: int
    line_total: Decimal
    
    class Config:
        from_attributes = True


# --- Заказы ---

class OrderBase(BaseModel):
    """Общие поля заказа."""
    client_id: int
    currency: str = Field("KZT", max_length=10)
    delivery_address: Optional[str] = None
    delivery_date: Optional[datetime] = None
    notes: Optional[str] = None


class OrderCreate(OrderBase):
    """Схема для создания заказа с позициями."""
    items: list[OrderItemCreate] = Field(..., min_length=1)


class OrderUpdate(BaseModel):
    """Схема для обновления заказа."""
    client_id: Optional[int] = None
    status: Optional[str] = None
    currency: Optional[str] = None
    delivery_address: Optional[str] = None
    delivery_date: Optional[datetime] = None
    notes: Optional[str] = None


class OrderRead(OrderBase):
    """Схема для чтения заказа."""
    id: int
    order_number: str
    status: str
    total_amount: Decimal
    order_date: datetime
    created_at: datetime
    updated_at: datetime
    
    # Вложенные данные
    items: list[OrderItemRead] = []
    
    # Рассчитываемые поля
    paid_amount: float = 0
    debt_amount: float = 0
    
    class Config:
        from_attributes = True


class OrderList(BaseModel):
    """Схема для списка заказов."""
    items: list[OrderRead]
    total: int
    page: int
    per_page: int
