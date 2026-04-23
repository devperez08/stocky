@echo off
title Stocky Launcher (Legacy Windows 7)
echo 🚀 Iniciando Stocky en modo nativo...

:: 1. Activar entorno virtual y lanzar Backend en segundo plano
echo 🔧 Iniciando motor de datos (Backend)...
start /min cmd /c "venv\Scripts\activate && uvicorn backend.app.main:app --host 0.0.0.0 --port 8000"

:: 2. Esperar un momento
timeout /t 6

:: 3. Lanzar la interfaz de usuario
echo 🖥️ Iniciando interfaz de usuario (Frontend)...
venv\Scripts\python.exe -m streamlit run frontend/app.py

echo ✅ Proceso iniciado. Si el navegador no abre, entra a: http://localhost:8501
