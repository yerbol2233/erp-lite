"""
Модель заказа.
Основной документ системы — заказ от клиента.
"""

from datetime import datetime
from sqlalchemy import Column, Integer, String, DateTime, Numeric, ForeignKey, Text
from sqlalchemy.orm import relationship

from db.database import Base


class Order(Base):
    """
    Таблица заказов.
    
    Заказ — центральная сущность системы.
    Связывает клиента с товарами и платежами.
    
    Статусы:
        - new: новый заказ
        - confirmed: подтверждён
        - in_progress: в работе
        - shipped: отгружен
        - completed: завершён
        - cancelled: отменён
    """
    __tablename__ = "orders"
    
    id = Column(Integer, primary_key=True, index=True)
    
    # Номер заказа (человекочитаемый)
    order_number = Column(String(50), unique=True, index=True)
    
    # Связь с клиентом
    client_id = Column(Integer, ForeignKey("clients.id"), nullable=False, index=True)
    
    # Статус и даты
    status = Column(String(50), default="new", index=True)
    order_date = Column(DateTime, default=datetime.utcnow)
    
    # Финансы
    total_amount = Column(Numeric(15, 2), default=0)  # Общая сумма
    currency = Column(String(10), default="KZT")
    
    # Доставка
    delivery_address = Column(Text, nullable=True)
    delivery_date = Column(DateTime, nullable=True)
    
    # Примечания
    notes = Column(Text, nullable=True)
    
    # Служебные поля
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Связи
    client = relationship("Client", back_populates="orders")
    items = relationship("OrderItem", back_populates="order", cascade="all, delete-orphan")
    payments = relationship("Payment", back_populates="order", cascade="all, delete-orphan")
    
    def __repr__(self):
        return f"<Order {self.order_number}>"
    
    @property
    def paid_amount(self) -> float:
        """Сумма всех оплат по заказу."""
        return sum(p.amount for p in self.payments if p.status == "completed")
    
    @property
    def debt_amount(self) -> float:
        """Задолженность по заказу."""
        return float(self.total_amount or 0) - self.paid_amount


class OrderItem(Base):
    """
    Таблица позиций заказа.
    
    Связка заказа с товаром: какой товар, сколько, по какой цене.
    """
    __tablename__ = "order_items"
    
    id = Column(Integer, primary_key=True, index=True)
    
    # Связи
    order_id = Column(Integer, ForeignKey("orders.id"), nullable=False, index=True)
    product_id = Column(Integer, ForeignKey("products.id"), nullable=False, index=True)
    
    # Количество и цена
    quantity = Column(Numeric(15, 3), nullable=False, default=1)
    unit_price = Column(Numeric(15, 2), nullable=False)  # Цена на момент заказа
    
    # Расчётная сумма
    line_total = Column(Numeric(15, 2), nullable=False)  # quantity * unit_price
    
    # Связи
    order = relationship("Order", back_populates="items")
    product = relationship("Product")
    
    def __repr__(self):
        return f"<OrderItem order={self.order_id} product={self.product_id}>"
