# 📘 Manual de Instalación y Uso de Stocky

Bienvenido al manual oficial de **Stocky**, el sistema inteligente de inventarios. Este documento te guiará paso a paso para instalar el sistema en tu computadora, comenzar a usarlo y configurarlo para que se abra automáticamente cuando enciendas tu equipo, ya sea en Windows o en Linux.

---

## 🛠️ Parte 1: Instalación Rápida (Recomendado con Docker)

El sistema está empaquetado para que funcione en cualquier equipo sin complicaciones de configuración, utilizando **Docker**.

### Requisitos Previos

Antes de instalar Stocky, necesitas asegurar que tienes estos programas:
1. **Git**: Para descargar los archivos del proyecto. [Descargar Git](https://git-scm.com/downloads)
2. **Docker Desktop**: Es el motor que arranca todo el sistema sin que tengas que instalar bases de datos o lenguajes de programación. [Descargar Docker Desktop](https://www.docker.com/products/docker-desktop/)

> **Tip Importante:** Durante la instalación de Docker, asegúrate de activar la opción que dice **"Start Docker Desktop when you log in"** (Iniciar Docker al arrancar la computadora). Esto es vital para la automatización.

### Paso a Paso para Instalar

1. **Descargar el sistema:** Abre una consola (Símbolo del sistema en Windows o Terminal en Linux) y escribe el siguiente comando:
   ```bash
   git clone https://github.com/devperez08/stocky.git
   cd stocky
   ```
2. **Primer Inicio:** Ejecuta el siguiente comando para levantar el sistema y prepararlo por primera vez:
   ```bash
   docker compose up -d --build
   ```
   *La primera vez que lo ejecutes tardará un poco porque estará descargando lo necesario. Las próximas veces será casi inmediato.*

---

## 🤖 Parte 2: Automatización del Encendido

Una vez que comprobaste que el sistema funciona, puedes configurarlo para que se abra solo cada vez que enciendas tu PC y te lo muestre automáticamente en tu navegador web.

### 🪟 Para Sistemas Windows

Hemos preparado un archivo especial llamado `launcher_windows.bat` que arranca el sistema y abre tu navegador web. Para que esto suceda al iniciar sesión:

1. Busca el archivo `launcher_windows.bat` dentro de la carpeta `stocky` que descargaste.
2. Da clic derecho y selecciona **"Copiar"**.
3. Presiona en tu teclado las teclas `Windows + R` al mismo tiempo, esto abrirá una pequeña ventana llamada "Ejecutar".
4. Escribe exactamente **`shell:startup`** y presiona la tecla Enter.
5. Se abrirá una carpeta vacía. Da clic derecho en un espacio en blanco y selecciona **"Pegar acceso directo"** (es mejor pegar como acceso directo al archivo original).
6. ¡Listo! Al reiniciar tu Windows, el sistema abrirá la página automáticamente.

### 🐧 Para Sistemas Linux

Para sistemas basados en Linux (como Ubuntu), hemos provisto un script `run_stocky.sh`.

1. Abre una terminal dentro de la carpeta `stocky`.
2. Otorga permisos de ejecución al script si no los tiene:
   ```bash
   chmod +x run_stocky.sh
   ```
3. Ahora, lo agregaremos a los "Aplicaciones al inicio" (Startup Applications). Esto depende de tu entorno de escritorio (GNOME, KDE, etc.):
   - Presiona tu tecla de menú y busca **"Aplicaciones al inicio"** (o "Startup Applications").
   - Añade una nueva entrada.
   - **Nombre:** Stocky
   - **Comando:** Da explorar o escribe la ruta completa hacia el archivo `run_stocky.sh` (Ejemplo: `/home/tu_usuario/stocky/run_stocky.sh`).
   - Da clic a "Guardar".
4. ¡Listo! La próxima vez que inicies sesión en Linux, una terminal se abrirá en segundo plano y lanzará el sistema directamente en tu navegador por defecto.

---

## 🖥️ Parte 3: ¿Cómo Utilizar Stocky?

El sistema cuenta con un panel intuitivo localizado en: **http://localhost:8501**

### 1. Panel Principal (Dashboard)
Aquí podrás observar un resumen de qué tan bien van tus números: el total invertido en inventario, ventas, y qué productos están bajo inventario de manera gráfica.

### 2. Gestión de Categorías
Antes de agregar productos, es ideal que crees algunas categorías (Ej. "Lácteos", "Electrodomésticos", "Snacks"). Esto te ayudará a filtrar y encontrar tus cosas más adelante.

### 3. Gestión de Productos
En esta sección puedes ver, filtrar, y crear tu catálogo.
- **Crear Producto:** Dirígete a la pestaña "➕ Agregar Producto". Rellena los datos básicos. 
  *(Nota: El código de barras/SKU se autogenera internamente por el sistema mientras no dispongas de una pistola lectora, así que el formulario ahora no te pedirá que introduzcas el SKU manualmente, haciendo la carga más rápida).*
- **Editar/Desactivar:** Puedes dar de baja artículos o cambiar su precio/cantidad utilizando las pestañas correspondientes.

### 4. Entradas y Salidas (Movimientos)
Toda entrada de nuevo material al almacén o toda venta **debe** ser registrada aquí para que el total de inventario (Stock Actual) cambie de manera correcta:
- Si recibes mercancía, ingresa una **Entrada**.
- Si vendes un artículo, registra una **Salida** (y el dinero de la venta figurará ingresado).

### 5. Reportes
¡Evalúa tus ventas! Puedes establecer rangos de fechas (ej: revisar las ventas de este mes) y exportarlo a un archivo de Excel para entregarlo a tu contador o para guardarlo de manera personal.
