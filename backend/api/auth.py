"""
API маршруты авторизации.
Регистрация, вход и получение текущего пользователя.
"""

from datetime import timedelta
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session

from db.database import get_db
from core.config import get_settings
from core.security import verify_password, get_password_hash, create_access_token
from core.dependencies import get_current_user
from models import User
from schemas import UserCreate, UserRead, Token

router = APIRouter(prefix="/auth", tags=["Авторизация"])


@router.post("/register", response_model=UserRead, status_code=status.HTTP_201_CREATED)
def register(
    user_data: UserCreate,
    db: Session = Depends(get_db)
):
    """
    Регистрация нового пользователя.
    
    Проверяем, что email ещё не занят, хешируем пароль и сохраняем.
    """
    # Проверяем, нет ли уже такого email
    existing_user = db.query(User).filter(User.email == user_data.email).first()
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Пользователь с таким email уже существует"
        )
    
    # Создаём нового пользователя
    user = User(
        email=user_data.email,
        hashed_password=get_password_hash(user_data.password),
        full_name=user_data.full_name,
        role="viewer"  # Новые пользователи получают базовую роль
    )
    
    db.add(user)
    db.commit()
    db.refresh(user)
    
    return user


@router.post("/login", response_model=Token)
def login(
    form_data: OAuth2PasswordRequestForm = Depends(),
    db: Session = Depends(get_db)
):
    """
    Авторизация пользователя.
    
    Проверяем email/пароль и выдаём JWT-токен.
    Используем стандартную форму OAuth2 (username + password).
    """
    # Ищем пользователя по email (в форме OAuth2 поле называется username)
    user = db.query(User).filter(User.email == form_data.username).first()
    
    if not user or not verify_password(form_data.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Неверный email или пароль",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Пользователь деактивирован"
        )
    
    # Создаём токен — sub должен быть строкой согласно JWT-стандарту
    settings = get_settings()
    access_token = create_access_token(
        data={"sub": str(user.id)},  # Преобразуем ID в строку
        expires_delta=timedelta(minutes=settings.access_token_expire_minutes)
    )
    
    return {"access_token": access_token, "token_type": "bearer"}


@router.get("/me", response_model=UserRead)
def get_me(current_user: User = Depends(get_current_user)):
    """
    Получить данные текущего авторизованного пользователя.
    """
    return current_user
