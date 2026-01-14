/**
 * Конфигурация приложения.
 * API URL берётся из переменной окружения Vercel или используется локальный.
 */

// URL бэкенда - для локальной разработки замените на http://127.0.0.1:8000/api
const API_BASE_URL = 'https://erp-lite-backend-kgn5.onrender.com/api';

// Экспортируем конфигурацию
window.APP_CONFIG = {
    API_BASE_URL: API_BASE_URL,
};

// Для дебага
console.log('API URL:', API_BASE_URL);
