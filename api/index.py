"""
Точка входа для Vercel Serverless Functions.
Импортирует FastAPI приложение из backend.
"""

import sys
import os

# Добавляем backend в путь
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'backend'))

from main import app

# Vercel требует переменную с именем handler или app
app = app
