"""
Схемы клиентов для валидации.
"""

from datetime import datetime
from typing import Optional
from pydantic import BaseModel, EmailStr, Field


class ClientBase(BaseModel):
    """Общие поля клиента."""
    name: str = Field(..., min_length=1, max_length=255)
    company: Optional[str] = None
    phone: Optional[str] = None
    email: Optional[EmailStr] = None
    city: Optional[str] = None
    address: Optional[str] = None
    inn: Optional[str] = None
    notes: Optional[str] = None


class ClientCreate(ClientBase):
    """Схема для создания клиента."""
    pass


class ClientUpdate(BaseModel):
    """Схема для обновления клиента (все поля опциональны)."""
    name: Optional[str] = Field(None, min_length=1, max_length=255)
    company: Optional[str] = None
    phone: Optional[str] = None
    email: Optional[EmailStr] = None
    city: Optional[str] = None
    address: Optional[str] = None
    inn: Optional[str] = None
    notes: Optional[str] = None


class ClientRead(ClientBase):
    """Схема для чтения клиента (ответ API)."""
    id: int
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True


class ClientList(BaseModel):
    """Схема для списка клиентов с пагинацией."""
    items: list[ClientRead]
    total: int
    page: int
    per_page: int
