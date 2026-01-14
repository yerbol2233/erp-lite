/**
 * Конфигурация приложения.
 * Используем переменные окружения для разных сред (разработка/продакшен).
 */

// Получаем URL API из переменных окружения или используем значение по умолчанию
// window.ENV будет подставляться при деплое на Vercel через env.js
const API_BASE_URL = window.ENV?.API_BASE_URL || 'http://127.0.0.1:8000/api';

// Экспортируем конфигурацию
window.APP_CONFIG = {
    API_BASE_URL: API_BASE_URL,
};

// Для дебага
console.log('API URL:', API_BASE_URL);
