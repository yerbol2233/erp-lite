# 🚀 Быстрый старт: Развёртывание за 15 минут

![Архитектура развёртывания](/Users/erboltalipov/.gemini/antigravity/brain/46062c51-7d05-4a20-9c1d-5e59fb94fc68/deployment_diagram_1768385290704.png)

```
┌─────────────────────────────────────────────────────────┐
│              Архитектура развёртывания                   │
│                                                          │
│  ┌──────────────┐         ┌──────────────┐              │
│  │   Browser    │────────▶│   Vercel     │              │
│  │   (Клиент)   │         │  (Frontend)  │              │
│  └──────────────┘         └──────┬───────┘              │
│                                  │                       │
│                                  │ API Requests          │
│                                  ▼                       │
│                          ┌──────────────┐                │
│                          │   Railway    │                │
│                          │  (Backend)   │                │
│                          └──────┬───────┘                │
│                                  │                       │
│                                  ▼                       │
│                          ┌──────────────┐                │
│                          │  PostgreSQL  │                │
│                          │  (Database)  │                │
│                          └──────────────┘                │
└─────────────────────────────────────────────────────────┘
```

## ⚡️ За 3 шага

### 1️⃣ Развернуть бэкенд на Railway (5 минут)

```bash
# 1. Создайте аккаунт: https://railway.app
# 2. New Project → Deploy from GitHub
# 3. Выберите репозиторий
# 4. Settings → Root Directory: "backend"
# 5. New → Database → PostgreSQL
# 6. Variables → добавьте:
#    - SECRET_KEY: <сгенерированный ключ>
#    - CORS_ORIGINS: https://your-app.vercel.app
# 7. Settings → Networking → Generate Domain
# 8. Скопируйте URL (например: https://erp-backend.up.railway.app)
```

### 2️⃣ Развернуть фронтенд на Vercel (5 минут)

```bash
# 1. Создайте аккаунт: https://vercel.com
# 2. Import Project → выберите репозиторий
# 3. Root Directory: "frontend"
# 4. Environment Variables → добавьте:
#    - API_BASE_URL: https://erp-backend.up.railway.app/api
# 5. Deploy
# 6. Скопируйте URL (например: https://erp-lite.vercel.app)
```

### 3️⃣ Обновить CORS (2 минуты)

```bash
# В Railway:
# Variables → обновите CORS_ORIGINS:
# https://erp-lite.vercel.app,http://localhost:3000
# 
# Перезапустите приложение
```

---

## 🎯 Быстрая проверка

1. ✅ Откройте `https://ваш-backend.railway.app/docs` — должна быть API документация
2. ✅ Откройте `https://ваш-frontend.vercel.app` — должна быть страница входа
3. ✅ Зарегистрируйтесь и войдите в систему

---

## 📋 Чек-лист

### Бэкенд (Railway)
- [ ] Создан проект в Railway
- [ ] Подключен GitHub репозиторий
- [ ] Установлен Root Directory: `backend`
- [ ] Добавлена PostgreSQL база данных
- [ ] Добавлены переменные окружения (SECRET_KEY, CORS_ORIGINS)
- [ ] Сгенерирован публичный домен
- [ ] Доступна документация по адресу `/docs`

### Фронтенд (Vercel)
- [ ] Создан проект в Vercel
- [ ] Подключен GitHub репозиторий
- [ ] Установлен Root Directory: `frontend`
- [ ] Добавлена переменная `API_BASE_URL`
- [ ] Успешно задеплоен
- [ ] Открывается в браузере

### Интеграция
- [ ] CORS настроен на бэкенде
- [ ] Фронтенд может делать запросы к бэкенду
- [ ] Регистрация работает
- [ ] Вход работает
- [ ] Все страницы открываются

---

## 🛠 Альтернатива: Через CLI

### Вариант для разработчиков

```bash
# Бэкенд
cd backend
railway login
railway init
railway add --plugin postgresql
railway up
railway open

# Фронтенд
cd ../frontend
vercel login
vercel
vercel env add API_BASE_URL production
# Введите: https://ваш-railway-url.up.railway.app/api
vercel --prod
```

---

## 💡 Полезные команды

### Railway
```bash
railway login         # Авторизация
railway link          # Привязать к существующему проекту
railway up            # Деплой
railway logs          # Просмотр логов
railway open          # Открыть приложение
railway variables     # Посмотреть переменные
```

### Vercel
```bash
vercel login          # Авторизация
vercel                # Деплой (preview)
vercel --prod         # Деплой (production)
vercel logs           # Просмотр логов
vercel env ls         # Список переменных
vercel env add        # Добавить переменную
```

---

## 🔗 Ссылки

- [Полная инструкция](/DEPLOYMENT_GUIDE_RU.md)
- [Railway Deploy Guide](/backend/RAILWAY_DEPLOY_RU.md)
- [Vercel Deploy Guide](/frontend/DEPLOY_RU.md)

---

Готово! Теперь ваше приложение работает! 🎉
