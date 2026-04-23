#!/bin/bash

echo "🚀 Iniciando Stocky — Sistema de Inventarios..."

# Verificar si Docker está corriendo
if ! docker info > /dev/null 2>&1; then
    echo "❌ Error: Docker no parece estar iniciado. Por favor, abre Docker Desktop e inténtalo de nuevo."
    exit 1
fi

# Iniciar los contenedores en segundo plano
echo "📦 Levantando servicios..."
docker compose up -d --build

# Esperar a que el frontend esté listo
echo "⏳ Esperando a que el sistema esté listo (5 segundos)..."
sleep 5

# Abrir el navegador según el SO
if [[ "$OSTYPE" == "linux-gnu"* ]]; then
    xdg-open http://localhost:8501
elif [[ "$OSTYPE" == "darwin"* ]]; then
    open http://localhost:8501
elif [[ "$OSTYPE" == "cygwin" ]] || [[ "$OSTYPE" == "msys" ]] || [[ "$OSTYPE" == "win32" ]]; then
    start http://localhost:8501
else
    echo "⚠️  No pude abrir el navegador automáticamente. Por favor entra a: http://localhost:8501"
fi

echo "✅ Stocky está corriendo. ¡Disfruta!"
echo "Para detenerlo, usa: docker compose down"
