/**
 * Основной модуль приложения ERP-Lite.
 * Управление страницами, авторизацией и взаимодействием с пользователем.
 */

// Ссылки на DOM-элементы
const elements = {
    // Экраны
    authScreen: document.getElementById('auth-screen'),
    app: document.getElementById('app'),

    // Авторизация
    authTabs: document.querySelectorAll('.auth-tab'),
    loginForm: document.getElementById('login-form'),
    registerForm: document.getElementById('register-form'),
    loginError: document.getElementById('login-error'),
    registerError: document.getElementById('register-error'),

    // Навигация
    navItems: document.querySelectorAll('.nav-item'),
    pageTitle: document.getElementById('page-title'),
    pageActions: document.getElementById('page-actions'),
    pageContent: document.getElementById('page-content'),

    // Пользователь
    userInfo: document.getElementById('user-info'),
    logoutBtn: document.getElementById('logout-btn'),

    // Модальное окно
    modalOverlay: document.getElementById('modal-overlay'),
    modal: document.getElementById('modal'),
    modalTitle: document.getElementById('modal-title'),
    modalBody: document.getElementById('modal-body'),
    modalClose: document.getElementById('modal-close'),

    // Уведомления
    toastContainer: document.getElementById('toast-container'),
};

// Текущая страница
let currentPage = 'dashboard';

// ==========================================================================
// Инициализация приложения
// ==========================================================================

document.addEventListener('DOMContentLoaded', () => {
    initApp();
});

async function initApp() {
    // Проверяем авторизацию
    if (api.isAuthenticated()) {
        try {
            await loadCurrentUser();
            showApp();
        } catch (error) {
            // Токен невалидный — показываем форму входа
            showAuthScreen();
        }
    } else {
        showAuthScreen();
    }

    // Привязываем обработчики событий
    setupEventListeners();
}

// ==========================================================================
// Авторизация
// ==========================================================================

function showAuthScreen() {
    elements.authScreen.hidden = false;
    elements.app.hidden = true;
}

function showApp() {
    elements.authScreen.hidden = true;
    elements.app.hidden = false;

    // Загружаем начальную страницу
    navigateTo('dashboard');
}

async function loadCurrentUser() {
    const user = await api.getCurrentUser();

    // Отображаем информацию о пользователе в сайдбаре
    const userNameEl = elements.userInfo.querySelector('.user-name');
    const userRoleEl = elements.userInfo.querySelector('.user-role');

    userNameEl.textContent = user.full_name || user.email;
    userRoleEl.textContent = getRoleName(user.role);
}

function getRoleName(role) {
    const roles = {
        'admin': 'Администратор',
        'manager': 'Менеджер',
        'viewer': 'Наблюдатель',
    };
    return roles[role] || role;
}

// ==========================================================================
// Обработчики событий
// ==========================================================================

function setupEventListeners() {
    // Переключение вкладок авторизации
    elements.authTabs.forEach(tab => {
        tab.addEventListener('click', () => {
            const tabName = tab.dataset.tab;

            // Переключаем активную вкладку
            elements.authTabs.forEach(t => t.classList.remove('active'));
            tab.classList.add('active');

            // Показываем нужную форму
            if (tabName === 'login') {
                elements.loginForm.hidden = false;
                elements.registerForm.hidden = true;
            } else {
                elements.loginForm.hidden = true;
                elements.registerForm.hidden = false;
            }
        });
    });

    // Форма входа
    elements.loginForm.addEventListener('submit', async (e) => {
        e.preventDefault();

        const email = document.getElementById('login-email').value;
        const password = document.getElementById('login-password').value;
        const btn = elements.loginForm.querySelector('button[type="submit"]');

        try {
            setButtonLoading(btn, true);
            elements.loginError.textContent = '';

            await api.login(email, password);
            await loadCurrentUser();
            showApp();
            showToast('Добро пожаловать!', 'success');
        } catch (error) {
            elements.loginError.textContent = error.message;
        } finally {
            setButtonLoading(btn, false);
        }
    });

    // Форма регистрации
    elements.registerForm.addEventListener('submit', async (e) => {
        e.preventDefault();

        const name = document.getElementById('register-name').value;
        const email = document.getElementById('register-email').value;
        const password = document.getElementById('register-password').value;
        const btn = elements.registerForm.querySelector('button[type="submit"]');

        try {
            setButtonLoading(btn, true);
            elements.registerError.textContent = '';

            await api.register(email, password, name);
            await api.login(email, password);
            await loadCurrentUser();
            showApp();
            showToast('Регистрация успешна!', 'success');
        } catch (error) {
            elements.registerError.textContent = error.message;
        } finally {
            setButtonLoading(btn, false);
        }
    });

    // Навигация
    elements.navItems.forEach(item => {
        item.addEventListener('click', (e) => {
            e.preventDefault();
            const page = item.dataset.page;
            navigateTo(page);
        });
    });

    // Выход
    elements.logoutBtn.addEventListener('click', () => {
        api.clearToken();
        showAuthScreen();
        showToast('Вы вышли из системы', 'success');
    });

    // Закрытие модального окна
    elements.modalClose.addEventListener('click', closeModal);
    elements.modalOverlay.addEventListener('click', (e) => {
        if (e.target === elements.modalOverlay) {
            closeModal();
        }
    });

    // Закрытие по Escape
    document.addEventListener('keydown', (e) => {
        if (e.key === 'Escape' && !elements.modalOverlay.hidden) {
            closeModal();
        }
    });
}

// ==========================================================================
// Навигация между страницами
// ==========================================================================

async function navigateTo(page) {
    currentPage = page;

    // Обновляем активный пункт меню
    elements.navItems.forEach(item => {
        item.classList.toggle('active', item.dataset.page === page);
    });

    // Очищаем кнопки действий
    elements.pageActions.innerHTML = '';

    // Загружаем содержимое страницы
    switch (page) {
        case 'dashboard':
            await renderDashboard();
            break;
        case 'clients':
            await renderClients();
            break;
        case 'products':
            await renderProducts();
            break;
        case 'orders':
            await renderOrders();
            break;
        case 'payments':
            await renderPayments();
            break;
    }
}

// ==========================================================================
// Страница: Дашборд
// ==========================================================================

async function renderDashboard() {
    elements.pageTitle.textContent = 'Дашборд';

    try {
        const summary = await api.getSummary();

        elements.pageContent.innerHTML = `
            <div class="stats-grid">
                <div class="stat-card">
                    <div class="stat-label">Всего заказов</div>
                    <div class="stat-value">${summary.total_orders}</div>
                </div>
                <div class="stat-card">
                    <div class="stat-label">Выручка</div>
                    <div class="stat-value success">${formatMoney(summary.total_revenue)}</div>
                </div>
                <div class="stat-card">
                    <div class="stat-label">Задолженность</div>
                    <div class="stat-value warning">${formatMoney(summary.total_debt)}</div>
                </div>
                <div class="stat-card">
                    <div class="stat-label">Клиентов</div>
                    <div class="stat-value">${summary.total_clients}</div>
                </div>
                <div class="stat-card">
                    <div class="stat-label">Товаров</div>
                    <div class="stat-value">${summary.total_products}</div>
                </div>
            </div>
            
            <div class="table-container mb-lg" id="top-clients-container">
                <div class="table-header">
                    <h3 class="table-title">Топ клиентов</h3>
                </div>
                <div class="table-wrapper">
                    <table>
                        <thead>
                            <tr>
                                <th>Клиент</th>
                                <th class="text-right">Выручка</th>
                                <th class="text-right">Заказов</th>
                            </tr>
                        </thead>
                        <tbody id="top-clients-body">
                            <tr><td colspan="3" class="table-empty">Загрузка...</td></tr>
                        </tbody>
                    </table>
                </div>
            </div>
        `;

        // Загружаем топ клиентов
        loadTopClients();

    } catch (error) {
        elements.pageContent.innerHTML = `<p class="text-error">Ошибка загрузки: ${error.message}</p>`;
    }
}

async function loadTopClients() {
    const tbody = document.getElementById('top-clients-body');

    try {
        const clients = await api.getTopClients(5);

        if (clients.length === 0) {
            tbody.innerHTML = '<tr><td colspan="3" class="table-empty">Нет данных</td></tr>';
            return;
        }

        tbody.innerHTML = clients.map(c => `
            <tr>
                <td>${escapeHtml(c.client_name)}</td>
                <td class="text-right">${formatMoney(c.total_revenue)}</td>
                <td class="text-right">${c.orders_count}</td>
            </tr>
        `).join('');

    } catch (error) {
        tbody.innerHTML = `<tr><td colspan="3" class="text-error">Ошибка: ${error.message}</td></tr>`;
    }
}

// ==========================================================================
// Страница: Клиенты
// ==========================================================================

async function renderClients() {
    elements.pageTitle.textContent = 'Клиенты';

    // Кнопка добавления
    elements.pageActions.innerHTML = `
        <button class="btn btn-primary" id="add-client-btn">+ Добавить клиента</button>
    `;

    document.getElementById('add-client-btn').addEventListener('click', () => {
        openClientModal();
    });

    await loadClientsTable();
}

async function loadClientsTable() {
    elements.pageContent.innerHTML = `
        <div class="table-container">
            <div class="table-wrapper">
                <table>
                    <thead>
                        <tr>
                            <th>Имя</th>
                            <th>Компания</th>
                            <th>Телефон</th>
                            <th>Город</th>
                            <th>Действия</th>
                        </tr>
                    </thead>
                    <tbody id="clients-body">
                        <tr><td colspan="5" class="table-empty">Загрузка...</td></tr>
                    </tbody>
                </table>
            </div>
        </div>
    `;

    try {
        const response = await api.getClients();
        const clients = response.items;
        const tbody = document.getElementById('clients-body');

        if (clients.length === 0) {
            tbody.innerHTML = '<tr><td colspan="5" class="table-empty">Нет клиентов</td></tr>';
            return;
        }

        tbody.innerHTML = clients.map(c => `
            <tr>
                <td>${escapeHtml(c.name)}</td>
                <td>${escapeHtml(c.company || '-')}</td>
                <td>${escapeHtml(c.phone || '-')}</td>
                <td>${escapeHtml(c.city || '-')}</td>
                <td>
                    <button class="btn btn-sm btn-outline" onclick="openClientModal(${c.id})">✏️</button>
                    <button class="btn btn-sm btn-danger" onclick="deleteClient(${c.id})">🗑️</button>
                </td>
            </tr>
        `).join('');

    } catch (error) {
        document.getElementById('clients-body').innerHTML =
            `<tr><td colspan="5" class="text-error">Ошибка: ${error.message}</td></tr>`;
    }
}

async function openClientModal(clientId = null) {
    const isEdit = clientId !== null;
    let client = {};

    if (isEdit) {
        try {
            client = await api.getClient(clientId);
        } catch (error) {
            showToast(error.message, 'error');
            return;
        }
    }

    elements.modalTitle.textContent = isEdit ? 'Редактировать клиента' : 'Новый клиент';
    elements.modalBody.innerHTML = `
        <form id="client-form" class="modal-form">
            <div class="form-group">
                <label for="client-name">Имя *</label>
                <input type="text" id="client-name" value="${escapeHtml(client.name || '')}" required>
            </div>
            <div class="form-group">
                <label for="client-company">Компания</label>
                <input type="text" id="client-company" value="${escapeHtml(client.company || '')}">
            </div>
            <div class="form-group">
                <label for="client-phone">Телефон</label>
                <input type="text" id="client-phone" value="${escapeHtml(client.phone || '')}">
            </div>
            <div class="form-group">
                <label for="client-email">Email</label>
                <input type="email" id="client-email" value="${escapeHtml(client.email || '')}">
            </div>
            <div class="form-group">
                <label for="client-city">Город</label>
                <input type="text" id="client-city" value="${escapeHtml(client.city || '')}">
            </div>
            <div class="modal-actions">
                <button type="button" class="btn btn-outline" onclick="closeModal()">Отмена</button>
                <button type="submit" class="btn btn-primary">${isEdit ? 'Сохранить' : 'Создать'}</button>
            </div>
        </form>
    `;

    document.getElementById('client-form').addEventListener('submit', async (e) => {
        e.preventDefault();

        const data = {
            name: document.getElementById('client-name').value,
            company: document.getElementById('client-company').value || null,
            phone: document.getElementById('client-phone').value || null,
            email: document.getElementById('client-email').value || null,
            city: document.getElementById('client-city').value || null,
        };

        try {
            if (isEdit) {
                await api.updateClient(clientId, data);
                showToast('Клиент обновлён', 'success');
            } else {
                await api.createClient(data);
                showToast('Клиент создан', 'success');
            }
            closeModal();
            loadClientsTable();
        } catch (error) {
            showToast(error.message, 'error');
        }
    });

    openModal();
}

async function deleteClient(id) {
    if (!confirm('Удалить клиента?')) return;

    try {
        await api.deleteClient(id);
        showToast('Клиент удалён', 'success');
        loadClientsTable();
    } catch (error) {
        showToast(error.message, 'error');
    }
}

// ==========================================================================
// Страница: Товары
// ==========================================================================

async function renderProducts() {
    elements.pageTitle.textContent = 'Товары';

    elements.pageActions.innerHTML = `
        <button class="btn btn-primary" id="add-product-btn">+ Добавить товар</button>
    `;

    document.getElementById('add-product-btn').addEventListener('click', () => {
        openProductModal();
    });

    await loadProductsTable();
}

async function loadProductsTable() {
    elements.pageContent.innerHTML = `
        <div class="table-container">
            <div class="table-wrapper">
                <table>
                    <thead>
                        <tr>
                            <th>Название</th>
                            <th>Артикул</th>
                            <th class="text-right">Цена</th>
                            <th class="text-right">Остаток</th>
                            <th>Действия</th>
                        </tr>
                    </thead>
                    <tbody id="products-body">
                        <tr><td colspan="5" class="table-empty">Загрузка...</td></tr>
                    </tbody>
                </table>
            </div>
        </div>
    `;

    try {
        const response = await api.getProducts();
        const products = response.items;
        const tbody = document.getElementById('products-body');

        if (products.length === 0) {
            tbody.innerHTML = '<tr><td colspan="5" class="table-empty">Нет товаров</td></tr>';
            return;
        }

        tbody.innerHTML = products.map(p => `
            <tr>
                <td>${escapeHtml(p.name)}</td>
                <td>${escapeHtml(p.sku || '-')}</td>
                <td class="text-right">${formatMoney(p.price)} ${p.currency}</td>
                <td class="text-right">${p.stock_quantity} ${p.unit}</td>
                <td>
                    <button class="btn btn-sm btn-outline" onclick="openProductModal(${p.id})">✏️</button>
                    <button class="btn btn-sm btn-danger" onclick="deleteProduct(${p.id})">🗑️</button>
                </td>
            </tr>
        `).join('');

    } catch (error) {
        document.getElementById('products-body').innerHTML =
            `<tr><td colspan="5" class="text-error">Ошибка: ${error.message}</td></tr>`;
    }
}

async function openProductModal(productId = null) {
    const isEdit = productId !== null;
    let product = {};

    if (isEdit) {
        try {
            product = await api.getProduct(productId);
        } catch (error) {
            showToast(error.message, 'error');
            return;
        }
    }

    elements.modalTitle.textContent = isEdit ? 'Редактировать товар' : 'Новый товар';
    elements.modalBody.innerHTML = `
        <form id="product-form" class="modal-form">
            <div class="form-group">
                <label for="product-name">Название *</label>
                <input type="text" id="product-name" value="${escapeHtml(product.name || '')}" required>
            </div>
            <div class="form-group">
                <label for="product-sku">Артикул</label>
                <input type="text" id="product-sku" value="${escapeHtml(product.sku || '')}">
            </div>
            <div class="form-group">
                <label for="product-price">Цена *</label>
                <input type="number" id="product-price" value="${product.price || 0}" min="0" step="0.01" required>
            </div>
            <div class="form-group">
                <label for="product-stock">Остаток</label>
                <input type="number" id="product-stock" value="${product.stock_quantity || 0}" min="0" step="0.001">
            </div>
            <div class="modal-actions">
                <button type="button" class="btn btn-outline" onclick="closeModal()">Отмена</button>
                <button type="submit" class="btn btn-primary">${isEdit ? 'Сохранить' : 'Создать'}</button>
            </div>
        </form>
    `;

    document.getElementById('product-form').addEventListener('submit', async (e) => {
        e.preventDefault();

        const data = {
            name: document.getElementById('product-name').value,
            sku: document.getElementById('product-sku').value || null,
            price: parseFloat(document.getElementById('product-price').value),
            stock_quantity: parseFloat(document.getElementById('product-stock').value),
        };

        try {
            if (isEdit) {
                await api.updateProduct(productId, data);
                showToast('Товар обновлён', 'success');
            } else {
                await api.createProduct(data);
                showToast('Товар создан', 'success');
            }
            closeModal();
            loadProductsTable();
        } catch (error) {
            showToast(error.message, 'error');
        }
    });

    openModal();
}

async function deleteProduct(id) {
    if (!confirm('Удалить товар?')) return;

    try {
        await api.deleteProduct(id);
        showToast('Товар удалён', 'success');
        loadProductsTable();
    } catch (error) {
        showToast(error.message, 'error');
    }
}

// ==========================================================================
// Страница: Заказы
// ==========================================================================

async function renderOrders() {
    elements.pageTitle.textContent = 'Заказы';

    await loadOrdersTable();
}

async function loadOrdersTable() {
    elements.pageContent.innerHTML = `
        <div class="table-container">
            <div class="table-wrapper">
                <table>
                    <thead>
                        <tr>
                            <th>Номер</th>
                            <th>Дата</th>
                            <th>Статус</th>
                            <th class="text-right">Сумма</th>
                            <th class="text-right">Долг</th>
                        </tr>
                    </thead>
                    <tbody id="orders-body">
                        <tr><td colspan="5" class="table-empty">Загрузка...</td></tr>
                    </tbody>
                </table>
            </div>
        </div>
    `;

    try {
        const response = await api.getOrders();
        const orders = response.items;
        const tbody = document.getElementById('orders-body');

        if (orders.length === 0) {
            tbody.innerHTML = '<tr><td colspan="5" class="table-empty">Нет заказов</td></tr>';
            return;
        }

        tbody.innerHTML = orders.map(o => `
            <tr>
                <td>${escapeHtml(o.order_number)}</td>
                <td>${formatDate(o.order_date)}</td>
                <td>${getStatusBadge(o.status)}</td>
                <td class="text-right">${formatMoney(o.total_amount)} ${o.currency}</td>
                <td class="text-right ${o.debt_amount > 0 ? 'text-warning' : ''}">${formatMoney(o.debt_amount)}</td>
            </tr>
        `).join('');

    } catch (error) {
        document.getElementById('orders-body').innerHTML =
            `<tr><td colspan="5" class="text-error">Ошибка: ${error.message}</td></tr>`;
    }
}

function getStatusBadge(status) {
    const statuses = {
        'new': { label: 'Новый', class: 'badge-default' },
        'confirmed': { label: 'Подтверждён', class: 'badge-success' },
        'in_progress': { label: 'В работе', class: 'badge-warning' },
        'shipped': { label: 'Отгружен', class: 'badge-success' },
        'completed': { label: 'Завершён', class: 'badge-success' },
        'cancelled': { label: 'Отменён', class: 'badge-error' },
    };
    const s = statuses[status] || { label: status, class: 'badge-default' };
    return `<span class="badge ${s.class}">${s.label}</span>`;
}

// ==========================================================================
// Страница: Платежи
// ==========================================================================

async function renderPayments() {
    elements.pageTitle.textContent = 'Платежи';

    await loadPaymentsTable();
}

async function loadPaymentsTable() {
    elements.pageContent.innerHTML = `
        <div class="table-container">
            <div class="table-wrapper">
                <table>
                    <thead>
                        <tr>
                            <th>ID</th>
                            <th>Заказ</th>
                            <th>Дата</th>
                            <th>Тип</th>
                            <th class="text-right">Сумма</th>
                            <th>Статус</th>
                        </tr>
                    </thead>
                    <tbody id="payments-body">
                        <tr><td colspan="6" class="table-empty">Загрузка...</td></tr>
                    </tbody>
                </table>
            </div>
        </div>
    `;

    try {
        const response = await api.getPayments();
        const payments = response.items;
        const tbody = document.getElementById('payments-body');

        if (payments.length === 0) {
            tbody.innerHTML = '<tr><td colspan="6" class="table-empty">Нет платежей</td></tr>';
            return;
        }

        tbody.innerHTML = payments.map(p => `
            <tr>
                <td>#${p.id}</td>
                <td>Заказ #${p.order_id}</td>
                <td>${formatDate(p.payment_date)}</td>
                <td>${getPaymentTypeName(p.payment_type)}</td>
                <td class="text-right">${formatMoney(p.amount)} ${p.currency}</td>
                <td>${getPaymentStatusBadge(p.status)}</td>
            </tr>
        `).join('');

    } catch (error) {
        document.getElementById('payments-body').innerHTML =
            `<tr><td colspan="6" class="text-error">Ошибка: ${error.message}</td></tr>`;
    }
}

function getPaymentTypeName(type) {
    const types = {
        'prepayment': 'Предоплата',
        'payment': 'Оплата',
        'refund': 'Возврат',
    };
    return types[type] || type;
}

function getPaymentStatusBadge(status) {
    const statuses = {
        'pending': { label: 'Ожидает', class: 'badge-warning' },
        'completed': { label: 'Проведён', class: 'badge-success' },
        'cancelled': { label: 'Отменён', class: 'badge-error' },
    };
    const s = statuses[status] || { label: status, class: 'badge-default' };
    return `<span class="badge ${s.class}">${s.label}</span>`;
}

// ==========================================================================
// Модальные окна
// ==========================================================================

function openModal() {
    elements.modalOverlay.hidden = false;
    document.body.style.overflow = 'hidden';
}

function closeModal() {
    elements.modalOverlay.hidden = true;
    document.body.style.overflow = '';
}

// ==========================================================================
// Уведомления (Toast)
// ==========================================================================

function showToast(message, type = 'success') {
    const toast = document.createElement('div');
    toast.className = `toast ${type}`;
    toast.innerHTML = `
        <span>${escapeHtml(message)}</span>
    `;

    elements.toastContainer.appendChild(toast);

    // Автоматически скрываем через 3 секунды
    setTimeout(() => {
        toast.remove();
    }, 3000);
}

// ==========================================================================
// Вспомогательные функции
// ==========================================================================

function setButtonLoading(btn, loading) {
    const text = btn.querySelector('.btn-text');
    const loader = btn.querySelector('.btn-loader');

    if (loading) {
        btn.disabled = true;
        if (text) text.hidden = true;
        if (loader) loader.hidden = false;
    } else {
        btn.disabled = false;
        if (text) text.hidden = false;
        if (loader) loader.hidden = true;
    }
}

function formatMoney(amount) {
    const num = parseFloat(amount) || 0;
    return num.toLocaleString('ru-RU', {
        minimumFractionDigits: 0,
        maximumFractionDigits: 2
    });
}

function formatDate(dateString) {
    if (!dateString) return '-';
    const date = new Date(dateString);
    return date.toLocaleDateString('ru-RU');
}

function escapeHtml(text) {
    if (!text) return '';
    const div = document.createElement('div');
    div.textContent = text;
    return div.innerHTML;
}
