"""
Схемы товаров для валидации.
"""

from datetime import datetime
from decimal import Decimal
from typing import Optional
from pydantic import BaseModel, Field


class ProductBase(BaseModel):
    """Общие поля товара."""
    name: str = Field(..., min_length=1, max_length=255)
    sku: Optional[str] = Field(None, max_length=100)
    price: Decimal = Field(..., ge=0, description="Цена должна быть >= 0")
    currency: str = Field("KZT", max_length=10)
    unit: str = Field("шт", max_length=50)
    stock_quantity: Decimal = Field(0, ge=0)
    category: Optional[str] = None
    description: Optional[str] = None


class ProductCreate(ProductBase):
    """Схема для создания товара."""
    pass


class ProductUpdate(BaseModel):
    """Схема для обновления товара."""
    name: Optional[str] = Field(None, min_length=1, max_length=255)
    sku: Optional[str] = None
    price: Optional[Decimal] = Field(None, ge=0)
    currency: Optional[str] = None
    unit: Optional[str] = None
    stock_quantity: Optional[Decimal] = Field(None, ge=0)
    category: Optional[str] = None
    description: Optional[str] = None
    is_active: Optional[int] = None


class ProductRead(ProductBase):
    """Схема для чтения товара."""
    id: int
    is_active: int
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True


class ProductList(BaseModel):
    """Схема для списка товаров."""
    items: list[ProductRead]
    total: int
    page: int
    per_page: int
