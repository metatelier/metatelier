# 💎 MET-ATELIER — Luxury Boutique E-Commerce & CMS

> **Plataforma web de comercio electrónico y catálogo de alta costura, diseñada bajo una arquitectura monolítica modular en Django, con panel de administración desacoplado, motor de respaldo Git correlativo y servidor de producción de alto rendimiento optimizado para Windows.**

---

## 📋 Tabla de Contenidos
1. [Visión General del Proyecto](#-visión-general-del-proyecto)
2. [Stack Tecnológico y Versiones](#-stack-tecnológico-y-versiones)
3. [Arquitectura del Sistema](#-arquitectura-del-sistema)
4. [Estructura de Directorios](#-estructura-de-directorios)
5. [Guía de Instalación y Puesta en Marcha](#-guía-de-instalación-y-puesta-en-marcha)
   - [Requisitos Previos](#requisitos-previos)
   - [Configuración de Entorno](#configuración-de-entorno)
   - [Modo Desarrollo](#modo-desarrollo)
   - [Modo Producción](#modo-producción)
6. [Flujo de Trabajo y Componentes Clave](#-flujo-de-trabajo-y-componentes-clave)
   - [1. Configuración Visual Dinámica (Singleton `CONF_WEB`)](#1-configuración-visual-dinámica-singleton-conf_web)
   - [2. Catálogo y Carrito Desacoplado](#2-catálogo-y-carrito-desacoplado)
   - [3. Motor de Respaldos Git (GitHub Engine)](#3-motor-de-respaldos-git-github-engine)
   - [4. Despliegue Público (Cloudflare Tunnel)](#4-despliegue-público-cloudflare-tunnel)
7. [Panel de Administración y Credenciales](#-panel-de-administración-y-credenciales)

---

## 🌟 Visión General del Proyecto

**MET-ATELIER** es una boutique digital de artículos de moda de lujo (carteras, calzados, prendas y accesorios). El sistema está concebido para ofrecer:
* **Experiencia de usuario de alta fidelidad:** Carga inmediata estilo SPA sin frameworks frontend pesados, permitiendo navegación fluida, filtros por categorías, búsqueda en tiempo real y bolsa de compras interactiva.
* **Control total desde el navegador:** El propietario de la tienda puede personalizar tipografías, colores de acento, textos del hero y metadatos SEO sin necesidad de editar código fuente.
* **Resiliencia Operativa:** Arquitectura optimizada para operar en servidores locales sobre Windows, sirviendo archivos estáticos eficientemente y sincronizándose de forma continua y automatizada con **GitHub**.

---

## 🛠️ Stack Tecnológico y Versiones

| Componente | Tecnología | Versión | Propósito |
| :--- | :--- | :---: | :--- |
| **Backend Core** | Python | `3.14.7` | Lenguaje base del servidor |
| **Framework Web** | Django | `6.1` | Lógica de negocio, ORM y enrutamiento |
| **Servidor WSGI** | Waitress | `3.0.2` | Servidor de producción multihilo nativo para Windows |
| **Archivos Estáticos** | Whitenoise | `6.12.0` | Compresión, cacheo y entrega de assets sin Nginx |
| **Base de Datos** | SQLite3 | `3.x` | Base de datos relacional ligera y portable |
| **Procesamiento de Fotos** | Pillow | `12.3.0` | Manejo y subida de imágenes de productos |
| **Frontend** | Vanilla JS / CSS3 / HTML5 | Modern ES6+ | Interfaz de usuario dinámica sin dependencias de Node.js |
| **Túnel Seguro** | Cloudflare Zero Trust | Latest | Publicación a internet (`https://met-atelier.store`) |

---

## 📐 Arquitectura del Sistema

El proyecto sigue una arquitectura **Clean MVC / Services-driven**:

```
[ Cliente / Navegador Web ]
           │
           ▼
[ Cloudflare Zero Trust Tunnel ] (https://met-atelier.store)
           │
           ▼
[ Waitress WSGI Server ] (Puerto 8080, 8 hilos concurrentes)
           │
           ├──► [ Whitenoise Middleware ] ──► Sirve /static/ y /staticfiles/
           │
           └──► [ Django Core Router (LuxuryMonsei.urls) ]
                       │
                       ▼
           [ Controladores Modulares (modelos/views/) ]
                       │
                       ├──► [ catalog_service ] ──► Base de Datos SQLite (CONF_WEB, PRODUCTO)
                       │
                       └──► [ git_service ]     ──► Repositorio Git (Commits correlativos y Push a GitHub)
```

---

## 📂 Estructura de Directorios

```text
MET/
├── .env.example                  # Plantilla para variables de entorno (PORT, DEBUG, SECRET_KEY)
├── .gitignore                    # Reglas de exclusión de Git (caches, logs, temporales)
├── requirements.txt              # Manifiesto de dependencias exactas del proyecto
├── manage.py                     # Entrada CLI estándar de Django
├── servidor_produccion.py        # Punto de entrada para Waitress en producción (puerto 8080)
├── respaldo_automatico.bat       # Script por lotes para el cron/tarea programada de Windows
├── db.sqlite3                    # Base de datos relacional activa
│
├── LuxuryMonsei/                 # Módulo de Configuración Principal del Proyecto (Core)
│   ├── settings.py               # Ajustes globales, lectura ligera de .env, Whitenoise, CORS y hosts
│   ├── urls.py                   # Enrutador raíz: delega a /admin/ y a modelos.urls
│   ├── wsgi.py                   # Conector WSGI para Waitress
│   ├── asgi.py                   # Conector ASGI opcional
│   └── __init__.py
│
├── modelos/                      # Aplicación Principal de Negocio
│   ├── models.py                 # Esquema de datos: CONF_WEB, CATEGORIA, PRODUCTO, IMG_PRODUCTO, PEDIDO
│   ├── admin.py                  # Registro e interfaz para el Django Admin tradicional
│   ├── apps.py                   # Configuración de la aplicación
│   ├── urls.py                   # Rutas de API JSON y vistas web
│   │
│   ├── services/                 # Capa de Lógica de Negocio y Utilidades Puras
│   │   ├── catalog_service.py    # Extracción de menús, productos y armado de contexto web
│   │   └── git_service.py        # Motor de comandos Git, versionado 'vX.Y.Z', bloqueo SQLite y rollback
│   │
│   └── views/                    # Controladores Modulares Desacoplados
│       ├── __init__.py           # Re-exportador para compatibilidad 100% de importaciones
│       ├── web_views.py          # Renderizado de la plantilla HTML principal (Index)
│       ├── api_auth.py           # Verificación de credenciales y PIN administrativo
│       ├── api_catalog.py        # Endpoints /api/productos y /api/textos
│       ├── api_orders.py         # Endpoints /api/pedidos para clientes y buzón de admin
│       └── api_git.py            # Endpoints /api/git/backup, versions y restore
│
├── templates/                    # Vistas HTML Semánticas
│   ├── index.html                # Plantilla ensambladora raíz
│   └── includes/                 # Componentes Modulares Reutilizables
│       ├── header.html           # Barra superior, marca, búsqueda y acceso a bolsa
│       ├── hero.html             # Portada de bienvenida y versículos dinámicos
│       ├── catalog.html          # Grilla de piezas de lujo y filtros de categoría
│       ├── footer.html           # Pie de página de alta costura y enlaces
│       ├── cart_drawer.html      # Carrito deslizante lateral
│       ├── modals_shop.html      # Modal de detalle de producto y modal de checkout
│       └── modal_admin.html      # Panel administrativo (Inventario, Buzón y Respaldos GIT)
│
├── static/                       # Archivos estáticos fuente de desarrollo (CSS, JS, Logo)
├── staticfiles/                  # Archivos estáticos recolectados y optimizados para producción
├── productos/                    # Fotografías activas de las piezas del catálogo
│
└── docs/                         # Documentación y registros históricos
    └── logs_historicos/          # Diagnósticos previos y consolas de depuración
```

---

## 🚀 Guía de Instalación y Puesta en Marcha

### Requisitos Previos
* Windows 10/11 o Windows Server (64-bit).
* Python `3.12` o superior instalado y agregado al `PATH`.
* Git para Windows instalado y configurado con acceso SSH a GitHub.

### 1. Clonar el Repositorio
```bash
git clone git@github.com:metatelier/metatelier.git
cd metatelier
```

### 2. Instalar Dependencias
```bash
pip install -r requirements.txt
```

### 3. Configurar Entorno (Opcional)
Si deseas personalizar el puerto o claves, copia `.env.example`:
```bash
copy .env.example .env
```

---

### 4. Modo Desarrollo
Para realizar pruebas con recarga en caliente (*Hot-Reload*):
```bash
python manage.py runserver 8000
```
La aplicación estará disponible en `http://127.0.0.1:8000`.

---

### 5. Modo Producción (Recomendado)
Para iniciar el servidor definitivo multihilo con Waitress en el puerto `8080`:
```bash
python servidor_produccion.py
```
> **Nota:** Mantén abierta la ventana de la consola para garantizar que el servidor continúe en ejecución.

---

## 🔄 Flujo de Trabajo y Componentes Clave

### 1. Configuración Visual Dinámica (Singleton `CONF_WEB`)
En `modelos/models.py`, el modelo `CONF_WEB` almacena una única fila que centraliza todos los parámetros editables del sitio:
* Si la base de datos es nueva o está vacía, el servicio `get_menu_config()` inicializa automáticamente una fila por defecto para evitar errores `IndexError`.
* El frontend inyecta estas variables como propiedades CSS (`--font-title`, `--font-body`) y textos del Hero, Meta Tags y Pie de página.

### 2. Catálogo y Carrito Desacoplado
* **Carga Inicial Asistida:** Django renderiza el catálogo en el servidor (SSR) para indexación SEO y velocidad inicial.
* **Interacción Cliente:** [static/app.js](file:///c:/Users/Carlos%20Enyerve/Desktop/PROYECTOS/MET/static/app.js) toma el control, permitiendo filtrar en vivo por etiquetas, gestionar la bolsa en `localStorage` y enviar solicitudes de adquisición mediante `POST /api/pedidos`.

### 3. Motor de Respaldos Git (GitHub Engine)
El sistema incluye integración nativa con Git a través de [modelos/services/git_service.py](file:///c:/Users/Carlos%20Enyerve/Desktop/PROYECTOS/MET/modelos/services/git_service.py):
* **`💾 Crear Copia GIT`:**
  1. Detecta la última versión en el historial (ej. `v1.2.8`).
  2. Calcula correlativamente la siguiente (`v1.2.9`).
  3. Ejecuta `git add .`, genera el commit y realiza `git push origin main`.
* **`📥 Restaurar GIT`:**
  1. Lista los commits disponibles en el selector desplegable.
  2. Al ordenar la restauración, invoca `connections.close_all()` para **liberar el candado exclusivo de `db.sqlite3` en Windows**.
  3. Ejecuta `git checkout <hash> -- .` y crea un commit con la secuencia de versiones para **nunca perder historial ni romper la rama principal**.
  4. Sincroniza archivos con `collectstatic` y recarga la página.

### 4. Despliegue Público (Cloudflare Tunnel)
El servidor corre localmente en el puerto `8080` y se conecta con el exterior a través del servicio de Windows **`Cloudflared agent`**, el cual establece un túnel cifrado hacia el dominio configurado sin necesidad de abrir puertos en routers (NAT traversal).

---

## 🔐 Panel de Administración y Credenciales

### 1. Panel de Administración Tradicional de Django
* **URL:** `http://localhost:8080/admin/`
* **Superusuarios activos:** `Dorimar` o `root`.
* **Gestión disponible:** Modelos `CONF_WEB`, `CATEGORIA`, `PRODUCTO`, `IMG_PRODUCTO`, `PEDIDO`.

### 2. Panel Administrativo en la Web (Atelier Concierge)
* **Acceso:** Hacer clic en el ícono del candado en la cabecera de la tienda.
* **PIN de Acceso por Defecto:** `G89qpjksr**` (Configurable desde el modelo `CONF_WEB`).
* **Pestañas:**
  1. **Buzón:** Solicitudes de compra de clientes con cambio de estado.
  2. **Inventario:** Creación y edición de piezas con galería de imágenes múltiples.
  3. **Respaldos GIT:** Generación de copias y restauración con 1 clic hacia/desde GitHub.

---
*Documentación elaborada bajo estándares de Arquitectura Senior. Para soporte o extensiones, referirse a los módulos desacoplados en `modelos/services/`.*
