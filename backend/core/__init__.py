"""
Модуль core — ядро приложения.
Содержит конфигурацию, безопасность и общие зависимости.
"""

from .config import get_settings, Settings

__all__ = ["get_settings", "Settings"]
