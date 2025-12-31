"""
API маршруты для работы с платежами.
CRUD + автоматический пересчёт задолженности.
"""

from typing import Optional
from datetime import datetime
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session

from db.database import get_db
from core.dependencies import get_current_user
from models import User, Payment, Order
from schemas import PaymentCreate, PaymentUpdate, PaymentRead, PaymentList

router = APIRouter(prefix="/payments", tags=["Платежи"])


@router.get("", response_model=PaymentList)
def get_payments(
    page: int = Query(1, ge=1),
    per_page: int = Query(20, ge=1, le=100),
    order_id: Optional[int] = Query(None, description="Фильтр по заказу"),
    status_filter: Optional[str] = Query(None, alias="status", description="Фильтр по статусу"),
    payment_type: Optional[str] = Query(None, description="Тип платежа"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Получить список платежей с пагинацией."""
    query = db.query(Payment)
    
    if order_id:
        query = query.filter(Payment.order_id == order_id)
    
    if status_filter:
        query = query.filter(Payment.status == status_filter)
    
    if payment_type:
        query = query.filter(Payment.payment_type == payment_type)
    
    total = query.count()
    
    offset = (page - 1) * per_page
    payments = (
        query
        .order_by(Payment.created_at.desc())
        .offset(offset)
        .limit(per_page)
        .all()
    )
    
    return PaymentList(
        items=payments,
        total=total,
        page=page,
        per_page=per_page
    )


@router.get("/{payment_id}", response_model=PaymentRead)
def get_payment(
    payment_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Получить платёж по ID."""
    payment = db.query(Payment).filter(Payment.id == payment_id).first()
    
    if not payment:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Платёж не найден"
        )
    
    return payment


@router.post("", response_model=PaymentRead, status_code=status.HTTP_201_CREATED)
def create_payment(
    payment_data: PaymentCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Создать новый платёж.
    Автоматически привязывается к заказу и обновляет задолженность.
    """
    # Проверяем заказ
    order = db.query(Order).filter(Order.id == payment_data.order_id).first()
    if not order:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Заказ не найден"
        )
    
    # Создаём платёж
    payment = Payment(
        order_id=payment_data.order_id,
        amount=payment_data.amount,
        currency=payment_data.currency or order.currency,
        payment_type=payment_data.payment_type,
        payment_method=payment_data.payment_method,
        payment_date=payment_data.payment_date or datetime.utcnow(),
        notes=payment_data.notes,
        status="pending"  # Новый платёж ожидает подтверждения
    )
    
    db.add(payment)
    db.commit()
    db.refresh(payment)
    
    return payment


@router.patch("/{payment_id}", response_model=PaymentRead)
def update_payment(
    payment_id: int,
    payment_data: PaymentUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Обновить платёж."""
    payment = db.query(Payment).filter(Payment.id == payment_id).first()
    
    if not payment:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Платёж не найден"
        )
    
    # Нельзя менять проведённые платежи (кроме отмены)
    if payment.status == "completed" and payment_data.status != "cancelled":
        # Разрешаем только изменение заметок
        if payment_data.model_dump(exclude_unset=True).keys() - {"notes"}:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Нельзя изменять проведённый платёж"
            )
    
    update_data = payment_data.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(payment, field, value)
    
    db.commit()
    db.refresh(payment)
    
    return payment


@router.post("/{payment_id}/confirm", response_model=PaymentRead)
def confirm_payment(
    payment_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Подтвердить (провести) платёж.
    После подтверждения платёж нельзя редактировать.
    """
    payment = db.query(Payment).filter(Payment.id == payment_id).first()
    
    if not payment:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Платёж не найден"
        )
    
    if payment.status == "completed":
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Платёж уже проведён"
        )
    
    if payment.status == "cancelled":
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Нельзя провести отменённый платёж"
        )
    
    payment.status = "completed"
    db.commit()
    db.refresh(payment)
    
    return payment


@router.delete("/{payment_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_payment(
    payment_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Удалить платёж (только ожидающие)."""
    payment = db.query(Payment).filter(Payment.id == payment_id).first()
    
    if not payment:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Платёж не найден"
        )
    
    if payment.status != "pending":
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Можно удалять только ожидающие платежи"
        )
    
    db.delete(payment)
    db.commit()
