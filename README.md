# 📦 Stocky — Sistema Inteligente de Inventarios

![Docker](https://img.shields.io/badge/Docker-2496ED?style=for-the-badge&logo=docker&logoColor=white)
![Python](https://img.shields.io/badge/Python-3776AB?style=for-the-badge&logo=python&logoColor=white)
![FastAPI](https://img.shields.io/badge/FastAPI-005571?style=for-the-badge&logo=fastapi)
![Streamlit](https://img.shields.io/badge/Streamlit-FF4B4B?style=for-the-badge&logo=Streamlit&logoColor=white)

**Stocky** es una solución multi-tenant diseñada para pequeños y medianos negocios que buscan profesionalizar su control de stock, registrar ventas y visualizar el rendimiento financiero en tiempo real.

---

## 🚀 Inicio Rápido (Recomendado: Docker)

La forma más sencilla de poner Stocky en marcha es usando **Docker**.

### ⚠️ Requisitos Obligatorios
Antes de empezar, asegúrate de tener instalados estos dos programas:
1.  **Git**: [Descargar aquí](https://git-scm.com/downloads) (Para descargar el código).
2.  **Docker Desktop**: [Descargar aquí](https://www.docker.com/products/docker-desktop/) (El motor que corre el programa). 
    *   *Nota: Una vez instalado, asegúrate de que Docker esté ABIERTO antes de correr Stocky.*

### Paso 1: Clonar el Proyecto
Abre una terminal en la carpeta donde quieras guardar el programa y ejecuta:
```bash
git clone https://github.com/devperez08/stocky.git
cd stocky
```

### Paso 2: Iniciar Stocky
Ejecuta el comando mágico:
```bash
docker compose up -d --build
```

3. **¡Listo!** El sistema se abrirá automáticamente:
   - **Interfaz (Dashboard):** [http://localhost:8501](http://localhost:8501)
   - **Documentación API:** [http://localhost:8000/docs](http://localhost:8000/docs)

### ✨ Automatización Total (Windows)
Si quieres que Stocky se abra **solo** al encender la computadora:
1. Localiza el archivo `launcher_windows.bat` en la carpeta del proyecto.
2. Presiona `Win + R`, escribe `shell:startup` y presiona Enter.
3. Copia el archivo `launcher_windows.bat` (o crea un acceso directo) y pégalo en esa carpeta que se abrió.
4. ¡Eso es todo! La próxima vez que prendas el PC, Stocky se iniciará y abrirá el navegador por ti.

---

## 🛠️ Instalación Local (Desarrolladores)

Si prefieres correrlo directamente con Python:

### 1. Preparar el entorno:
```bash
# Crear y activar entorno virtual
python -m venv venv
source venv/bin/activate  # En Windows: venv\Scripts\activate

# Instalar dependencias
pip install -r requirements.txt
```

### 2. Ejecutar servicios:
Necesitas abrir **dos terminales**:

- **Terminal 1 (Backend):**
  ```bash
  uvicorn backend.app.main:app --reload
  ```
- **Terminal 2 (Frontend):**
  ```bash
  streamlit run frontend/app.py
  ```

---

## 📁 Estructura del Proyecto

```text
├── backend/            # Lógica central (FastAPI + SQLAlchemy)
├── frontend/           # Interfaz de usuario (Streamlit)
├── scripts/            # Utilidades (Seed de datos, reset de DB)
├── stocky.db           # Base de datos SQLite (Local)
└── docker-compose.yml  # Orquestación de contenedores
```

---

## 🧹 Mantenimiento

- **Limpiar base de datos:** Si quieres empezar de cero, usa `python scripts/reset_db.py`.
- **Poblar con datos demo:** Para ver cómo luce el sistema con data, usa `python scripts/seed_data.py`.

---

## ✨ Características Principales
- ✅ **Dashboard en tiempo real:** KPIs financieros y de stock.
- ✅ **Gestión de Productos:** CRUD completo con soporte de categorías.
- ✅ **Movimientos:** Registro de entradas y salidas con validación de stock.
- ✅ **Reportes:** Exportación a CSV y Excel con análisis financiero.

---
*Desarrollado con ❤️ por el equipo de Stocky.*
