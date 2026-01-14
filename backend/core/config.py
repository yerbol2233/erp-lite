"""
Конфигурация приложения.
Загружаем настройки из переменных окружения через pydantic-settings.
"""

from functools import lru_cache
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """
    Основные настройки приложения.
    Значения подтягиваются из .env файла или переменных окружения.
    """
    
    # Название и версия сервиса
    app_name: str = "ERP-Lite"
    app_version: str = "0.1.0"
    
    # Подключение к базе данных
    # В продакшене Railway автоматически устанавливает DATABASE_URL
    database_url: str = "sqlite:///./database.db"
    
    # JWT-настройки
    secret_key: str = "change-me-in-production"
    algorithm: str = "HS256"
    access_token_expire_minutes: int = 60
    
    # Режим отладки
    debug: bool = False
    
    # CORS — разрешённые источники
    cors_origins: str = "http://localhost:3000"
    
    @property
    def cors_origins_list(self) -> list[str]:
        """Преобразуем строку с хостами в список."""
        return [origin.strip() for origin in self.cors_origins.split(",")]
    
    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"


@lru_cache
def get_settings() -> Settings:
    """
    Кешированная функция для получения настроек.
    Создаём Settings один раз и переиспользуем.
    """
    return Settings()
