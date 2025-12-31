"""
API маршруты для работы с клиентами.
CRUD-операции: создание, чтение, обновление, удаление.
"""

from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session

from db.database import get_db
from core.dependencies import get_current_user
from models import User, Client
from schemas import ClientCreate, ClientUpdate, ClientRead, ClientList

router = APIRouter(prefix="/clients", tags=["Клиенты"])


@router.get("", response_model=ClientList)
def get_clients(
    page: int = Query(1, ge=1, description="Номер страницы"),
    per_page: int = Query(20, ge=1, le=100, description="Записей на странице"),
    search: Optional[str] = Query(None, description="Поиск по имени или компании"),
    city: Optional[str] = Query(None, description="Фильтр по городу"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Получить список клиентов с пагинацией и фильтрами.
    """
    query = db.query(Client)
    
    # Фильтр по поиску
    if search:
        search_pattern = f"%{search}%"
        query = query.filter(
            (Client.name.ilike(search_pattern)) | 
            (Client.company.ilike(search_pattern))
        )
    
    # Фильтр по городу
    if city:
        query = query.filter(Client.city == city)
    
    # Считаем общее количество
    total = query.count()
    
    # Применяем пагинацию
    offset = (page - 1) * per_page
    clients = query.order_by(Client.created_at.desc()).offset(offset).limit(per_page).all()
    
    return ClientList(
        items=clients,
        total=total,
        page=page,
        per_page=per_page
    )


@router.get("/{client_id}", response_model=ClientRead)
def get_client(
    client_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Получить клиента по ID."""
    client = db.query(Client).filter(Client.id == client_id).first()
    
    if not client:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Клиент не найден"
        )
    
    return client


@router.post("", response_model=ClientRead, status_code=status.HTTP_201_CREATED)
def create_client(
    client_data: ClientCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Создать нового клиента."""
    client = Client(**client_data.model_dump())
    
    db.add(client)
    db.commit()
    db.refresh(client)
    
    return client


@router.patch("/{client_id}", response_model=ClientRead)
def update_client(
    client_id: int,
    client_data: ClientUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Обновить данные клиента."""
    client = db.query(Client).filter(Client.id == client_id).first()
    
    if not client:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Клиент не найден"
        )
    
    # Обновляем только переданные поля
    update_data = client_data.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(client, field, value)
    
    db.commit()
    db.refresh(client)
    
    return client


@router.delete("/{client_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_client(
    client_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Удалить клиента."""
    client = db.query(Client).filter(Client.id == client_id).first()
    
    if not client:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Клиент не найден"
        )
    
    # Проверяем, нет ли связанных заказов
    if client.orders.count() > 0:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Нельзя удалить клиента с заказами"
        )
    
    db.delete(client)
    db.commit()
