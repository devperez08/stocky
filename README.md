# 📦 Stocky — Edición Windows 7 (Legacy)

Esta versión de Stocky está optimizada para equipos antiguos que no pueden ejecutar Docker Desktop. Utiliza una instalación nativa de Python para garantizar la máxima compatibilidad.

---

## 🚀 Requisitos de Instalación (Solo una vez)

Debes instalar los siguientes programas antes de comenzar:

1.  **Python 3.8**: [Descargar instalador de 64 bits](https://www.python.org/ftp/python/3.8.10/python-3.8.10-amd64.exe)
    - _Importante:_ En la instalación, marca la casilla que dice **"Add Python 3.8 to PATH"**.
2.  **Git**: [Descargar aquí](https://git-scm.com/download/win)

---

## 🛠️ Configuración Inicial

Abre una terminal (CMD) y sigue estos pasos por única vez:

1.  **Clonar el código:**

    ```bash
    git clone https://github.com/devperez08/stocky.git -b win7
    cd stocky
    ```

2.  **Crear el Entorno Virtual:**

    ```bash
    python -m venv venv
    ```

3.  **Instalar Dependencias:**
    ```bash
    venv\Scripts\pip install -r requirements.txt
    ```

---

## ✨ Automatización (Iniciar al prender la PC)

Para que el programa se abra solo y **sin ventanas negras estorbando**:

1.  Localiza el archivo **`silencioso.vbs`** en la carpeta del proyecto.
2.  Hazle clic derecho y selecciona **"Crear acceso directo"**.
3.  Presiona `Inicio` > `Todos los programas` > Haz clic derecho en la carpeta **"Inicio"** y selecciona **"Abrir"**.
4.  Pega el acceso directo que creaste dentro de esa carpeta.

¡Listo! Al entrar a Windows, el sistema correrá en segundo plano y abrirá tu navegador automáticamente.

---

## ⚙️ Uso Manual

Si solo quieres abrirlo de vez en cuando, simplemente haz doble clic en `launcher_win7.bat`.

---

_Nota: Se recomienda mantener actualizado el navegador Chrome o Edge en Windows 7 para una mejor experiencia visual._
