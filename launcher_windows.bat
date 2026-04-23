@echo off
:: Lanzador Automático de Stocky para Windows

echo 🚀 Iniciando Stocky - Sistema de Inventarios...

:: 1. Intentar levantar los contenedores (en segundo plano)
docker compose up -d

:: 2. Esperar 8 segundos para asegurar que el servidor este listo
echo ⏳ Esperando respuesta del servidor...
timeout /t 8 /nobreak > nul

:: 3. Abrir el navegador automaticamente
echo 🌐 Abriendo Dashboard en tu navegador...
start http://localhost:8501

echo ✅ Todo listo. ¡A vender!
pause
