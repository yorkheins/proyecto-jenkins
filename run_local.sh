#!/bin/bash
set -e

echo "📦 Instalando dependencias..."
pip install -r requirements.txt

echo ""
echo "🧪 Ejecutando pruebas..."
pytest tests/ --cov=app --cov-report=term-missing

echo ""
echo "🚀 Iniciando la aplicación en http://localhost:8000"
echo "📖 Documentación en http://localhost:8000/docs"
uvicorn app.app:app --host 0.0.0.0 --port 8000 --reload
