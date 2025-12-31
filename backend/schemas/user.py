"""
Схемы пользователей для валидации через Pydantic.
Используются в API для входящих/исходящих данных.
"""

from datetime import datetime
from typing import Optional
from pydantic import BaseModel, EmailStr, Field


# --- Базовые схемы ---

class UserBase(BaseModel):
    """Общие поля для всех схем пользователя."""
    email: EmailStr
    full_name: Optional[str] = None


class UserCreate(UserBase):
    """Схема для создания пользователя (регистрация)."""
    password: str = Field(..., min_length=6, description="Минимум 6 символов")


class UserUpdate(BaseModel):
    """Схема для обновления пользователя (все поля опциональны)."""
    email: Optional[EmailStr] = None
    full_name: Optional[str] = None
    password: Optional[str] = Field(None, min_length=6)
    role: Optional[str] = None
    is_active: Optional[bool] = None


class UserRead(UserBase):
    """Схема для чтения пользователя (ответ API)."""
    id: int
    role: str
    is_active: bool
    created_at: datetime
    
    class Config:
        from_attributes = True  # Разрешаем создание из ORM-модели


# --- Авторизация ---

class Token(BaseModel):
    """JWT-токен, возвращаемый при логине."""
    access_token: str
    token_type: str = "bearer"


class TokenData(BaseModel):
    """Данные из расшифрованного токена."""
    email: Optional[str] = None
    user_id: Optional[int] = None


class LoginRequest(BaseModel):
    """Запрос на авторизацию."""
    email: EmailStr
    password: str
