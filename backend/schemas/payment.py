"""
Схемы платежей для валидации.
"""

from datetime import datetime
from decimal import Decimal
from typing import Optional
from pydantic import BaseModel, Field


class PaymentBase(BaseModel):
    """Общие поля платежа."""
    order_id: int
    amount: Decimal = Field(..., gt=0, description="Сумма должна быть > 0")
    currency: str = Field("KZT", max_length=10)
    payment_type: str = Field("payment", description="prepayment, payment, refund")
    payment_method: Optional[str] = None
    payment_date: Optional[datetime] = None
    notes: Optional[str] = None


class PaymentCreate(PaymentBase):
    """Схема для создания платежа."""
    pass


class PaymentUpdate(BaseModel):
    """Схема для обновления платежа."""
    amount: Optional[Decimal] = Field(None, gt=0)
    currency: Optional[str] = None
    payment_type: Optional[str] = None
    status: Optional[str] = None
    payment_method: Optional[str] = None
    payment_date: Optional[datetime] = None
    notes: Optional[str] = None


class PaymentRead(PaymentBase):
    """Схема для чтения платежа."""
    id: int
    status: str
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True


class PaymentList(BaseModel):
    """Схема для списка платежей."""
    items: list[PaymentRead]
    total: int
    page: int
    per_page: int
