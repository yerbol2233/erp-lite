/**
 * Конфигурация приложения.
 * Используем переменные окружения для разных сред (разработка/продакшен).
 */

// Получаем URL API из переменных окружения или используем значение по умолчанию
// window.ENV будет подставляться при деплое на Vercel через env.js (если используется)
const API_BASE_URL = window.ENV?.API_BASE_URL || 'https://erp-lite-backend-kgn5.onrender.com/api';

// Экспортируем конфигурацию
window.APP_CONFIG = {
    API_BASE_URL: API_BASE_URL,
};

// Для дебага
console.log('API URL:', API_BASE_URL);
