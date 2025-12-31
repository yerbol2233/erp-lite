"""
API маршруты для работы с заказами.
CRUD + расчёт суммы заказа и работа с позициями.
"""

from typing import Optional
from datetime import datetime
from decimal import Decimal
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session, joinedload

from db.database import get_db
from core.dependencies import get_current_user
from models import User, Order, OrderItem, Client, Product
from schemas import OrderCreate, OrderUpdate, OrderRead, OrderList

router = APIRouter(prefix="/orders", tags=["Заказы"])


def generate_order_number(db: Session) -> str:
    """
    Генерируем номер заказа.
    Формат: ORD-YYYYMMDD-XXXX (например, ORD-20251231-0001)
    """
    today = datetime.utcnow().strftime("%Y%m%d")
    prefix = f"ORD-{today}-"
    
    # Ищем последний заказ за сегодня
    last_order = (
        db.query(Order)
        .filter(Order.order_number.like(f"{prefix}%"))
        .order_by(Order.order_number.desc())
        .first()
    )
    
    if last_order:
        # Извлекаем номер и увеличиваем
        last_num = int(last_order.order_number.split("-")[-1])
        new_num = last_num + 1
    else:
        new_num = 1
    
    return f"{prefix}{new_num:04d}"


def calculate_order_total(items: list[OrderItem]) -> Decimal:
    """Считаем общую сумму заказа по позициям."""
    return sum(item.line_total for item in items)


@router.get("", response_model=OrderList)
def get_orders(
    page: int = Query(1, ge=1),
    per_page: int = Query(20, ge=1, le=100),
    client_id: Optional[int] = Query(None, description="Фильтр по клиенту"),
    status_filter: Optional[str] = Query(None, alias="status", description="Фильтр по статусу"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Получить список заказов с пагинацией."""
    query = db.query(Order).options(joinedload(Order.items))
    
    if client_id:
        query = query.filter(Order.client_id == client_id)
    
    if status_filter:
        query = query.filter(Order.status == status_filter)
    
    total = query.count()
    
    offset = (page - 1) * per_page
    orders = (
        query
        .order_by(Order.created_at.desc())
        .offset(offset)
        .limit(per_page)
        .all()
    )
    
    # Добавляем расчётные поля
    order_reads = []
    for order in orders:
        order_read = OrderRead.model_validate(order)
        order_read.paid_amount = order.paid_amount
        order_read.debt_amount = order.debt_amount
        order_reads.append(order_read)
    
    return OrderList(
        items=order_reads,
        total=total,
        page=page,
        per_page=per_page
    )


@router.get("/{order_id}", response_model=OrderRead)
def get_order(
    order_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Получить заказ по ID с позициями."""
    order = (
        db.query(Order)
        .options(joinedload(Order.items))
        .filter(Order.id == order_id)
        .first()
    )
    
    if not order:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Заказ не найден"
        )
    
    order_read = OrderRead.model_validate(order)
    order_read.paid_amount = order.paid_amount
    order_read.debt_amount = order.debt_amount
    
    return order_read


@router.post("", response_model=OrderRead, status_code=status.HTTP_201_CREATED)
def create_order(
    order_data: OrderCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Создать новый заказ с позициями.
    Автоматически рассчитывается сумма и генерируется номер.
    """
    # Проверяем, существует ли клиент
    client = db.query(Client).filter(Client.id == order_data.client_id).first()
    if not client:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Клиент не найден"
        )
    
    # Создаём заказ
    order = Order(
        order_number=generate_order_number(db),
        client_id=order_data.client_id,
        currency=order_data.currency,
        delivery_address=order_data.delivery_address,
        delivery_date=order_data.delivery_date,
        notes=order_data.notes,
    )
    
    db.add(order)
    db.flush()  # Получаем ID заказа
    
    # Добавляем позиции
    for item_data in order_data.items:
        # Проверяем товар
        product = db.query(Product).filter(Product.id == item_data.product_id).first()
        if not product:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Товар с ID {item_data.product_id} не найден"
            )
        
        # Рассчитываем сумму позиции
        line_total = item_data.quantity * item_data.unit_price
        
        order_item = OrderItem(
            order_id=order.id,
            product_id=item_data.product_id,
            quantity=item_data.quantity,
            unit_price=item_data.unit_price,
            line_total=line_total
        )
        db.add(order_item)
    
    db.flush()
    
    # Считаем общую сумму
    order.total_amount = calculate_order_total(order.items)
    
    db.commit()
    db.refresh(order)
    
    return order


@router.patch("/{order_id}", response_model=OrderRead)
def update_order(
    order_id: int,
    order_data: OrderUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Обновить заказ (без позиций)."""
    order = db.query(Order).filter(Order.id == order_id).first()
    
    if not order:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Заказ не найден"
        )
    
    # Проверяем нового клиента, если меняется
    if order_data.client_id:
        client = db.query(Client).filter(Client.id == order_data.client_id).first()
        if not client:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Клиент не найден"
            )
    
    update_data = order_data.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(order, field, value)
    
    db.commit()
    db.refresh(order)
    
    return order


@router.delete("/{order_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_order(
    order_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Удалить заказ (только новые без платежей)."""
    order = (
        db.query(Order)
        .options(joinedload(Order.payments))
        .filter(Order.id == order_id)
        .first()
    )
    
    if not order:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Заказ не найден"
        )
    
    # Проверяем, нет ли платежей
    if order.payments:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Нельзя удалить заказ с платежами"
        )
    
    # Можно удалять только новые заказы
    if order.status not in ("new", "cancelled"):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Можно удалять только новые или отменённые заказы"
        )
    
    db.delete(order)
    db.commit()
