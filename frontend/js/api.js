/**
 * API-клиент для работы с сервером ERP-Lite.
 * Обёртка над fetch с авторизацией и обработкой ошибок.
 */

// Получаем URL API из конфигурации (config.js)
// const API_BASE_URL = window.APP_CONFIG?.API_BASE_URL; // Берем из глобальной конфигурации

/**
 * Класс для работы с API.
 * Автоматически добавляет токен авторизации к запросам.
 */
class ApiClient {
    constructor() {
        // Токен хранится в localStorage
        this.token = localStorage.getItem('auth_token');
        this.baseUrl = window.APP_CONFIG?.API_BASE_URL || 'https://erp-lite-backend-kgn5.onrender.com/api';
    }

    /**
     * Сохраняем токен после успешной авторизации.
     * @param {string} token - JWT токен
     */
    setToken(token) {
        this.token = token;
        localStorage.setItem('auth_token', token);
    }

    /**
     * Удаляем токен при выходе из системы.
     */
    clearToken() {
        this.token = null;
        localStorage.removeItem('auth_token');
    }

    /**
     * Проверяем, авторизован ли пользователь.
     * @returns {boolean}
     */
    isAuthenticated() {
        return !!this.token;
    }

    /**
     * Базовый метод для выполнения HTTP-запросов.
     * @param {string} endpoint - путь API (без базового URL)
     * @param {Object} options - опции fetch (method, body и т.д.)
     * @returns {Promise<Object>} - ответ сервера в JSON
     */
    async request(endpoint, options = {}) {
        const url = `${this.baseUrl}${endpoint}`;

        // Формируем заголовки
        const headers = {
            'Content-Type': 'application/json',
            ...options.headers,
        };

        // Добавляем токен авторизации
        if (this.token) {
            headers['Authorization'] = `Bearer ${this.token}`;
        }

        // Выполняем запрос
        const response = await fetch(url, {
            ...options,
            headers,
            body: options.body ? JSON.stringify(options.body) : undefined,
        });

        // Обрабатываем ошибки HTTP
        if (!response.ok) {
            // Если 401 — сбрасываем токен
            if (response.status === 401) {
                this.clearToken();
            }

            // Пытаемся получить текст ошибки из ответа
            let errorMessage = `Ошибка ${response.status}`;
            try {
                const errorData = await response.json();
                errorMessage = errorData.detail || errorMessage;
            } catch {
                // Если не удалось распарсить JSON — оставляем общую ошибку
            }

            throw new Error(errorMessage);
        }

        // Если 204 No Content — возвращаем null
        if (response.status === 204) {
            return null;
        }

        return response.json();
    }

    // --- Авторизация ---

    /**
     * Регистрация нового пользователя.
     */
    async register(email, password, fullName) {
        return this.request('/auth/register', {
            method: 'POST',
            body: { email, password, full_name: fullName },
        });
    }

    /**
     * Авторизация пользователя.
     * Возвращает токен доступа.
     */
    async login(email, password) {
        // Формируем данные в формате x-www-form-urlencoded
        const formData = new URLSearchParams();
        formData.append('username', email);
        formData.append('password', password);

        const response = await fetch(`${this.baseUrl}/auth/login`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/x-www-form-urlencoded',
            },
            body: formData,
        });

        if (!response.ok) {
            let errorMessage = 'Ошибка авторизации';
            try {
                const errorData = await response.json();
                errorMessage = errorData.detail || errorMessage;
            } catch { }
            throw new Error(errorMessage);
        }

        const data = await response.json();
        this.setToken(data.access_token);
        return data;
    }

    /**
     * Получить текущего пользователя.
     */
    async getCurrentUser() {
        return this.request('/auth/me');
    }

    // --- Клиенты ---

    /**
     * Получить список клиентов.
     */
    async getClients(params = {}) {
        const query = new URLSearchParams(params).toString();
        return this.request(`/clients?${query}`);
    }

    /**
     * Получить клиента по ID.
     */
    async getClient(id) {
        return this.request(`/clients/${id}`);
    }

    /**
     * Создать нового клиента.
     */
    async createClient(data) {
        return this.request('/clients', {
            method: 'POST',
            body: data,
        });
    }

    /**
     * Обновить клиента.
     */
    async updateClient(id, data) {
        return this.request(`/clients/${id}`, {
            method: 'PATCH',
            body: data,
        });
    }

    /**
     * Удалить клиента.
     */
    async deleteClient(id) {
        return this.request(`/clients/${id}`, {
            method: 'DELETE',
        });
    }

    // --- Товары ---

    async getProducts(params = {}) {
        const query = new URLSearchParams(params).toString();
        return this.request(`/products?${query}`);
    }

    async getProduct(id) {
        return this.request(`/products/${id}`);
    }

    async createProduct(data) {
        return this.request('/products', {
            method: 'POST',
            body: data,
        });
    }

    async updateProduct(id, data) {
        return this.request(`/products/${id}`, {
            method: 'PATCH',
            body: data,
        });
    }

    async deleteProduct(id) {
        return this.request(`/products/${id}`, {
            method: 'DELETE',
        });
    }

    // --- Заказы ---

    async getOrders(params = {}) {
        const query = new URLSearchParams(params).toString();
        return this.request(`/orders?${query}`);
    }

    async getOrder(id) {
        return this.request(`/orders/${id}`);
    }

    async createOrder(data) {
        return this.request('/orders', {
            method: 'POST',
            body: data,
        });
    }

    async updateOrder(id, data) {
        return this.request(`/orders/${id}`, {
            method: 'PATCH',
            body: data,
        });
    }

    async deleteOrder(id) {
        return this.request(`/orders/${id}`, {
            method: 'DELETE',
        });
    }

    // --- Платежи ---

    async getPayments(params = {}) {
        const query = new URLSearchParams(params).toString();
        return this.request(`/payments?${query}`);
    }

    async getPayment(id) {
        return this.request(`/payments/${id}`);
    }

    async createPayment(data) {
        return this.request('/payments', {
            method: 'POST',
            body: data,
        });
    }

    async confirmPayment(id) {
        return this.request(`/payments/${id}/confirm`, {
            method: 'POST',
        });
    }

    async deletePayment(id) {
        return this.request(`/payments/${id}`, {
            method: 'DELETE',
        });
    }

    // --- Отчёты ---

    /**
     * Получить общую сводку (дашборд).
     */
    async getSummary() {
        return this.request('/reports/summary');
    }

    /**
     * Получить выручку по дням.
     */
    async getRevenueByPeriod(days = 30) {
        return this.request(`/reports/revenue-by-period?days=${days}`);
    }

    /**
     * Получить топ клиентов.
     */
    async getTopClients(limit = 10) {
        return this.request(`/reports/top-clients?limit=${limit}`);
    }

    /**
     * Получить клиентов с задолженностью.
     */
    async getDebts(minDebt = 0) {
        return this.request(`/reports/debts?min_debt=${minDebt}`);
    }
}

// Создаём глобальный экземпляр API-клиента
const api = new ApiClient();
