"""
API маршруты для аналитических отчётов.
Сводные данные по финансам, клиентам и заказам.
"""

from datetime import datetime, timedelta
from typing import Optional
from decimal import Decimal
from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from sqlalchemy import func, case

from db.database import get_db
from core.dependencies import get_current_user
from models import User, Order, Payment, Client, Product
from pydantic import BaseModel

router = APIRouter(prefix="/reports", tags=["Отчёты"])


# --- Схемы ответов ---

class SummaryReport(BaseModel):
    """Общая сводка по системе."""
    total_orders: int
    total_revenue: float
    total_debt: float
    total_clients: int
    total_products: int


class RevenueByPeriod(BaseModel):
    """Выручка за период."""
    period: str
    revenue: float
    orders_count: int


class TopClient(BaseModel):
    """Топ клиент по выручке."""
    client_id: int
    client_name: str
    total_revenue: float
    orders_count: int


class DebtReport(BaseModel):
    """Задолженность по клиенту."""
    client_id: int
    client_name: str
    total_debt: float
    orders_count: int


# --- Эндпоинты ---

@router.get("/summary", response_model=SummaryReport)
def get_summary(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Общая сводка по системе.
    Количество заказов, выручка, задолженность, клиенты и товары.
    """
    # Считаем заказы
    total_orders = db.query(func.count(Order.id)).scalar() or 0
    
    # Считаем выручку (сумма проведённых платежей)
    total_revenue = (
        db.query(func.sum(Payment.amount))
        .filter(Payment.status == "completed")
        .scalar()
    ) or 0
    
    # Считаем общую задолженность
    # Сумма заказов минус сумма проведённых платежей
    orders_total = db.query(func.sum(Order.total_amount)).scalar() or 0
    total_debt = float(orders_total) - float(total_revenue)
    
    # Количество клиентов и товаров
    total_clients = db.query(func.count(Client.id)).scalar() or 0
    total_products = (
        db.query(func.count(Product.id))
        .filter(Product.is_active == 1)
        .scalar()
    ) or 0
    
    return SummaryReport(
        total_orders=total_orders,
        total_revenue=float(total_revenue),
        total_debt=max(0, total_debt),  # Не показываем отрицательную задолженность
        total_clients=total_clients,
        total_products=total_products
    )


@router.get("/revenue-by-period", response_model=list[RevenueByPeriod])
def get_revenue_by_period(
    days: int = Query(30, ge=1, le=365, description="Количество дней"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Выручка по дням за последние N дней.
    """
    start_date = datetime.utcnow() - timedelta(days=days)
    
    # Группируем платежи по дням
    results = (
        db.query(
            func.date(Payment.payment_date).label("period"),
            func.sum(Payment.amount).label("revenue"),
            func.count(Payment.id).label("count")
        )
        .filter(
            Payment.status == "completed",
            Payment.payment_date >= start_date
        )
        .group_by(func.date(Payment.payment_date))
        .order_by(func.date(Payment.payment_date))
        .all()
    )
    
    return [
        RevenueByPeriod(
            period=str(r.period),
            revenue=float(r.revenue),
            orders_count=r.count
        )
        for r in results
    ]


@router.get("/top-clients", response_model=list[TopClient])
def get_top_clients(
    limit: int = Query(10, ge=1, le=50, description="Количество клиентов"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Топ клиентов по выручке.
    """
    # Суммируем платежи по клиентам через связь с заказами
    results = (
        db.query(
            Client.id,
            Client.name,
            func.sum(Payment.amount).label("revenue"),
            func.count(func.distinct(Order.id)).label("orders")
        )
        .join(Order, Order.client_id == Client.id)
        .join(Payment, Payment.order_id == Order.id)
        .filter(Payment.status == "completed")
        .group_by(Client.id, Client.name)
        .order_by(func.sum(Payment.amount).desc())
        .limit(limit)
        .all()
    )
    
    return [
        TopClient(
            client_id=r.id,
            client_name=r.name,
            total_revenue=float(r.revenue) if r.revenue else 0,
            orders_count=r.orders
        )
        for r in results
    ]


@router.get("/debts", response_model=list[DebtReport])
def get_debts(
    min_debt: float = Query(0, ge=0, description="Минимальная сумма задолженности"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Клиенты с задолженностью.
    Показываем только тех, у кого задолженность больше указанного порога.
    """
    # Подзапрос для суммы платежей по заказу
    paid_subq = (
        db.query(
            Payment.order_id,
            func.sum(Payment.amount).label("paid")
        )
        .filter(Payment.status == "completed")
        .group_by(Payment.order_id)
        .subquery()
    )
    
    # Считаем задолженность по клиентам
    results = (
        db.query(
            Client.id,
            Client.name,
            func.sum(Order.total_amount - func.coalesce(paid_subq.c.paid, 0)).label("debt"),
            func.count(Order.id).label("orders")
        )
        .join(Order, Order.client_id == Client.id)
        .outerjoin(paid_subq, paid_subq.c.order_id == Order.id)
        .group_by(Client.id, Client.name)
        .having(func.sum(Order.total_amount - func.coalesce(paid_subq.c.paid, 0)) > min_debt)
        .order_by(func.sum(Order.total_amount - func.coalesce(paid_subq.c.paid, 0)).desc())
        .all()
    )
    
    return [
        DebtReport(
            client_id=r.id,
            client_name=r.name,
            total_debt=float(r.debt) if r.debt else 0,
            orders_count=r.orders
        )
        for r in results
    ]
