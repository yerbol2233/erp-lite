"""
FastAPI зависимости.
Функции для получения текущего пользователя и проверки прав доступа.
"""

from typing import Optional
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm import Session

from db.database import get_db
from core.security import decode_token
from models import User

# Схема авторизации через Bearer-токен
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/auth/login")


def get_current_user(
    token: str = Depends(oauth2_scheme),
    db: Session = Depends(get_db)
) -> User:
    """
    Получаем текущего авторизованного пользователя из JWT-токена.
    
    Raises:
        HTTPException: Если токен невалидный или пользователь не найден
    """
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Не удалось проверить учётные данные",
        headers={"WWW-Authenticate": "Bearer"},
    )
    
    # Декодируем токен
    payload = decode_token(token)
    if payload is None:
        raise credentials_exception
    
    # Получаем user_id из токена (хранится как строка согласно JWT-стандарту)
    sub = payload.get("sub")
    if sub is None:
        raise credentials_exception
    
    try:
        user_id = int(sub)
    except (ValueError, TypeError):
        raise credentials_exception
    
    # Ищем пользователя в БД
    user = db.query(User).filter(User.id == user_id).first()
    if user is None:
        raise credentials_exception
    
    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Пользователь деактивирован"
        )
    
    return user


def get_current_active_user(
    current_user: User = Depends(get_current_user)
) -> User:
    """Проверяем, что пользователь активен."""
    if not current_user.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Пользователь деактивирован"
        )
    return current_user


def get_admin_user(
    current_user: User = Depends(get_current_user)
) -> User:
    """
    Проверяем, что пользователь — администратор.
    
    Raises:
        HTTPException: Если пользователь не админ
    """
    if current_user.role != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Требуются права администратора"
        )
    return current_user


def get_optional_user(
    token: Optional[str] = Depends(oauth2_scheme),
    db: Session = Depends(get_db)
) -> Optional[User]:
    """
    Опциональная авторизация — можно и без токена.
    Используется для публичных эндпоинтов с расширенными правами для авторизованных.
    """
    if not token:
        return None
    
    try:
        return get_current_user(token, db)
    except HTTPException:
        return None
