"""
Модуль API — все маршруты FastAPI.
"""

from .auth import router as auth_router
from .clients import router as clients_router
from .products import router as products_router
from .orders import router as orders_router
from .payments import router as payments_router
from .reports import router as reports_router

__all__ = [
    "auth_router",
    "clients_router",
    "products_router",
    "orders_router",
    "payments_router",
    "reports_router",
]
