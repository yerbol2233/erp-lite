# ⚡️ Шпаргалка по развёртыванию

## 🚂 Railway (Бэкенд)

### Через Web интерфейс
1. https://railway.app → Login with GitHub
2. New Project → Deploy from GitHub repo
3. Settings → Root Directory: `backend`
4. New → Database → Add PostgreSQL
5. Variables:
   ```
   SECRET_KEY=<random-32-chars>
   CORS_ORIGINS=https://your-app.vercel.app
   ```
6. Settings → Networking → Generate Domain
7. Копируем URL: `https://xxx.up.railway.app`

### Через CLI
```bash
cd backend
railway login
railway init
railway add --plugin postgresql
railway up
railway open
```

---

## 🌐 Vercel (Фронтенд)

### Через Web интерфейс
1. https://vercel.com → Login with GitHub
2. New Project → Import from GitHub
3. Root Directory: `frontend`
4. Environment Variables:
   - KEY: `API_BASE_URL`
   - VALUE: `https://xxx.up.railway.app/api`
5. Deploy
6. Копируем URL: `https://xxx.vercel.app`

### Через CLI
```bash
cd frontend
vercel login
vercel
vercel env add API_BASE_URL production
# Вводим: https://xxx.up.railway.app/api
vercel --prod
```

---

## ⚙️ Финальная настройка

1. Railway → Variables → обновляем CORS_ORIGINS:
   ```
   CORS_ORIGINS=https://your-app.vercel.app,http://localhost:3000
   ```

2. Перезапускаем бэкенд (Deployments → Restart)

3. Открываем `https://your-app.vercel.app`

---

## 🔑 Генерация SECRET_KEY

```bash
python -c "import secrets; print(secrets.token_urlsafe(32))"
```

---

## ✅ Проверка

### Бэкенд
```bash
# Должен открыться Swagger
open https://your-backend.railway.app/docs
```

### Фронтенд
```bash
# Должна открыться страница входа
open https://your-frontend.vercel.app
```

### В консоли браузера (F12)
```javascript
console.log(window.ENV)
console.log(window.APP_CONFIG)
```

---

## 📊 Полезные команды

### Railway
```bash
railway logs              # Логи
railway variables         # Список переменных
railway connect postgres  # Подключиться к БД
railway status            # Статус
```

### Vercel
```bash
vercel logs              # Логи
vercel env ls            # Список переменных
vercel domains           # Домены
vercel list              # Список проектов
```

---

## 🐛 Решение проблем

### CORS Error
```bash
# Railway → Variables → добавить/обновить:
CORS_ORIGINS=https://your-app.vercel.app,http://localhost:3000

# Перезапустить Railway app
# Очистить кэш браузера: Cmd+Shift+R
```

### Failed to fetch
```bash
# 1. Проверить бэкенд работает:
open https://your-backend.railway.app/docs

# 2. Проверить API_BASE_URL в Vercel:
vercel env ls

# 3. Если неправильный - обновить и передеплоить:
vercel env add API_BASE_URL production
vercel --prod
```

### 404 на странице
```bash
# Проверить что есть vercel.json с настройкой rewrites
cat frontend/vercel.json
```

---

## 📱 После развёртывания

✅ `https://your-backend.railway.app/docs` — API документация  
✅ `https://your-frontend.vercel.app` — Ваше приложение  
✅ Railway Dashboard — https://railway.app/dashboard  
✅ Vercel Dashboard — https://vercel.com/dashboard  

---

## 🎯 Быстрые ссылки

- [QUICKSTART_RU.md](../QUICKSTART_RU.md) — 15 минут
- [DEPLOYMENT_GUIDE_RU.md](../DEPLOYMENT_GUIDE_RU.md) — Полная инструкция
- [Frontend Guide](../frontend/DEPLOY_RU.md)
- [Backend Guide](../backend/RAILWAY_DEPLOY_RU.md)
