@echo off
title Stocky Launcher (Legacy Windows 7)
echo 🚀 Iniciando Stocky en modo nativo...

:: 1. Lanzar Backend en segundo plano (/b evita abrir una nueva ventana)
echo 🔧 Iniciando motor de datos (Backend)...
start /b venv\Scripts\python.exe -m uvicorn backend.app.main:app --host 0.0.0.0 --port 8000

:: 2. Esperar un momento a que el motor arranque
echo ⏳ Esperando a que el motor arranque...
timeout /t 5

:: 3. Lanzar la interfaz de usuario
echo 🖥️ Iniciando interfaz de usuario (Frontend)...
venv\Scripts\python.exe -m streamlit run frontend/app.py

echo ✅ Proceso iniciado.
