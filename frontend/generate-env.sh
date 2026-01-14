#!/bin/bash
# Скрипт для генерации env.js из переменных окружения Vercel

cat \u003c\u003cEOF \u003e js/env.js
// Автоматически сгенерировано при деплое
window.ENV = {
  API_BASE_URL: '${API_BASE_URL:-http://127.0.0.1:8000/api}'
};
EOF

echo "✅ env.js создан с API_BASE_URL = ${API_BASE_URL}"
