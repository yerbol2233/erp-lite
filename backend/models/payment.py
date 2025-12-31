"""
Модель платежа/оплаты.
Фиксация денежных поступлений по заказам.
"""

from datetime import datetime
from sqlalchemy import Column, Integer, String, DateTime, Numeric, ForeignKey, Text
from sqlalchemy.orm import relationship

from db.database import Base


class Payment(Base):
    """
    Таблица платежей.
    
    Платёж привязан к заказу и фиксирует поступление денег.
    
    Типы платежей:
        - prepayment: предоплата (до отгрузки)
        - payment: оплата (после отгрузки)
        - refund: возврат
    
    Статусы:
        - pending: ожидает подтверждения
        - completed: проведён
        - cancelled: отменён
    """
    __tablename__ = "payments"
    
    id = Column(Integer, primary_key=True, index=True)
    
    # Связь с заказом
    order_id = Column(Integer, ForeignKey("orders.id"), nullable=False, index=True)
    
    # Сумма и валюта
    amount = Column(Numeric(15, 2), nullable=False)
    currency = Column(String(10), default="KZT")
    
    # Тип и статус
    payment_type = Column(String(50), default="payment")  # prepayment, payment, refund
    status = Column(String(50), default="pending")  # pending, completed, cancelled
    
    # Способ оплаты
    payment_method = Column(String(100), nullable=True)  # наличные, карта, перевод
    
    # Дата платежа
    payment_date = Column(DateTime, default=datetime.utcnow)
    
    # Примечания
    notes = Column(Text, nullable=True)
    
    # Служебные поля
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Связи
    order = relationship("Order", back_populates="payments")
    
    def __repr__(self):
        return f"<Payment {self.id} order={self.order_id} amount={self.amount}>"
