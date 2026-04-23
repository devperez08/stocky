@echo off
:: Lanzador Automático de Stocky para Windows
title Stocky Launcher

echo 🚀 Iniciando Stocky - Sistema de Inventarios...

:: 0. Verificar si Docker está instalado
where docker >nul 2>nul
if %errorlevel% neq 0 (
    echo ❌ ERROR: Docker no está instalado en este equipo.
    echo Por favor, instala Docker Desktop desde: https://www.docker.com/products/docker-desktop/
    pause
    exit
)

:: 1. Intentar levantar los contenedores (en segundo plano)
echo 📦 Levantando servicios de Stocky...
docker compose up -d

:: 2. Esperar 12 segundos para asegurar que el servidor este listo
echo ⏳ Esperando a que el sistema respire (12 segundos)...
timeout /t 12 /nobreak > nul

:: 3. Abrir el navegador automaticamente
echo 🌐 Abriendo Dashboard en tu navegador...
start http://localhost:8501

echo ✅ Todo listo. ¡A vender!
timeout /t 5
