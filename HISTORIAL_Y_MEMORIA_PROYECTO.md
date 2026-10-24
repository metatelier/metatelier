# 🧠 MEMORIA MAESTRA, HISTORIAL Y BITÁCORA TÉCNICA DEL PROYECTO
> **Documento de Continuidad para Inteligencia Artificial y Desarrolladores Humanos**  
> *Fecha de emisión:* 23 de Octubre de 2026  
> *Cliente / Propietario:* Carlos Enyerve (Met Atelier)  
> *Rol asignado:* Senior Software Architect & Lead Fullstack Engineer  

---

## ⚡ INSTRUCCIÓN DE INICIALIZACIÓN RÁPIDA (PARA FUTURAS SESIONES DE IA)

> [!IMPORTANT]
> **Si eres una Inteligencia Artificial (Antigravity, Claude, Cursor, ChatGPT) leyendo este archivo tras una nueva instalación o reinicio de PC:**
> *Lee este documento completo y asume inmediatamente el rol de Programador Senior y Tech Lead de Carlos Enyerve.*  
> *Ya conoces íntimamente la arquitectura, decisiones de diseño, contratos de datos, credenciales y soluciones a errores específicos de Windows implementadas en este proyecto. Continúa el desarrollo con máxima precisión, manteniendo cero regresiones y respetando la separación de capas.*

---

## 1. FICHA TÉCNICA Y REPOSITORIOS

| Parámetro | Detalle en Producción (`MET`) | Detalle en Plantilla (`PLANTILLA_ECOMMERCE`) |
| :--- | :--- | :--- |
| **Nombre Comercial** | MET \| ATELIER (Haute Maroquinerie) | Plantilla Universal Marca Blanca |
| **Dominio Público** | `https://met-atelier.store` | Configurable para cualquier dominio |
| **Backend Framework** | Python 3.14 / Django 6.1 | Python 3.14 / Django 6.1 |
| **Servidor WSGI Producción** | Waitress 3.0.2 (Multi-hilo) | Waitress 3.0.2 (Multi-hilo) |
| **Archivos Estáticos** | WhiteNoise 6.12.0 (Directo vía WSGI) | WhiteNoise 6.12.0 |
| **Frontend** | Vanilla JavaScript (ES6+), HTML5 Semántico, CSS3 | Vanilla JavaScript (ES6+), HTML5, CSS3 |
| **Base de Datos** | SQLite (`db.sqlite3`) | SQLite (`db.sqlite3`) limpia con datos semilla |
| **Puerto de Producción** | `http://127.0.0.1:8080/` | `http://127.0.0.1:8080/` (o personalizable) |
| **Puerto de Desarrollo** | `http://127.0.0.1:8000/` | `http://127.0.0.1:8000/` |
| **Repositorio GitHub** | `git@github.com:metatelier/metatelier.git` | Repositorio local limpio listo para nuevo origen |
| **Túnel de Acceso Web** | Cloudflare Tunnel (`Cloudflared agent` service) | Cloudflare Tunnel o Nginx |

---

## 2. CREDENCIALES Y SECRETOS DEL SISTEMA

### Tienda en Producción (`MET`):
* **PIN de Acceso Administrativo Rápido (Web):** `G89qpjksr**`  
  *(Se ingresa en el modal que se abre al hacer clic en el candado 🔒 del header. Se valida contra `CONF_WEB.admin_password` mediante el header HTTP `x-admin-pin`).*
* **Panel Django Admin (`/admin/`):**
  * Superusuario 1: `Dorimar` \| Contraseña: `G89qpjksr**`
  * Superusuario 2: `root`
* **Claves SSH de GitHub:**
  * Ubicación en Windows: `C:\Users\Carlos Enyerve\.ssh\`
  * Archivos clave: `id_metatelier` / `id_ed25519`
  * Host configurado en `~/.ssh/config`: autenticado con usuario `metatelier` en GitHub.

### Plantilla Reutilizable (`PLANTILLA_ECOMMERCE`):
* **PIN Web Inicial:** `1234`
* **Superusuario Django (`/admin/`):** `admin` \| Contraseña: `admin1234`

---

## 3. ARQUITECTURA DEL CÓDIGO Y SEPARACIÓN DE CAPAS

El proyecto fue refactorizado desde una estructura monolítica hacia una **arquitectura limpia modular por capas**:

```
PROYECTO/
├── LuxuryMonsei/               # CORE DEL PROYECTO DJANGO
│   ├── settings.py             # Configuración central; lee variables de .env con fallbacks seguros.
│   │                           # MEDIA_URL = '/', MEDIA_ROOT = BASE_DIR
│   ├── urls.py                 # Enrutamiento maestro (Admin de Django + rutas de app + static media)
│   ├── wsgi.py                 # Entry point WSGI estándar utilizado por Waitress
│   └── asgi.py                 # Entry point ASGI
│
├── modelos/                    # CAPA DE APLICACIÓN Y DOMINIO
│   ├── models.py               # Modelos ORM:
│   │                           # - CONF_WEB: Singleton de configuración estética, títulos, textos y PIN
│   │                           # - CATEGORIA: Clasificación y filtros dinámicos de piezas
│   │                           # - IMG_PRODUCTO: Imágenes de catálogo (upload_to='productos/')
│   │                           # - PRODUCTO: Piezas, precios USD, material, dimensiones, SKU y agotado
│   │                           # - PEDIDO: CRM de reservas de clientes (datos, JSON de items y estados)
│   │
│   ├── services/               # CAPA DE SERVICIOS (LÓGICA DE NEGOCIO AISLADA)
│   │   ├── catalog_service.py  # get_menu_config() (singleton a prueba de fallos) y get_site_context()
│   │   └── git_service.py      # Motor de control de versiones Git en GitHub:
│   │                           # - get_versions_list(): Lista los últimos commits con fecha y sujeto
│   │                           # - get_next_version(): Calcula versión correlativa vX.Y.Z
│   │                           # - create_backup(): git add, commit, allow-empty y push a GitHub
│   │                           # - restore_version(): Cierra SQLite, checkout al hash y auto-backup previo
│   │
│   ├── views/                  # CAPA DE CONTROLADORES MODULARES
│   │   ├── __init__.py         # Re-exportador universal para mantener compatibilidad total de imports
│   │   ├── web_views.py        # Vista pública TemplateView (Index)
│   │   ├── api_auth.py         # _is_admin(request) y api_admin_login (validación de PIN)
│   │   ├── api_catalog.py      # api_productos, api_productos_detail, api_textos
│   │   ├── api_orders.py       # api_pedidos, api_pedidos_detail (cambio de estado / eliminar)
│   │   └── api_git.py          # api_git_backup, api_git_versions, api_git_restore
│   │
│   └── urls.py                 # Mapeo de endpoints de la app
│
├── templates/                  # CAPA DE PRESENTACIÓN (COMPONENTES MODULARES)
│   ├── index.html              # Orquestador principal limpio (solo 60 líneas con {% include %})
│   └── includes/
│       ├── header.html         # Navbar, logotipo dinámico, candado de admin y contador de carrito
│       ├── hero.html           # Banner promocional principal e indicador de scroll
│       ├── catalog.html        # Filtros automáticos y grilla de productos
│       ├── footer.html         # Pie de página de alta costura, enlaces y copyright
│       ├── cart_drawer.html    # Drawer deslizante de la bolsa de compras
│       ├── modals_shop.html    # Modales de Detalle de Producto y Checkout Concierge
│       └── modal_admin.html    # Panel de administración (Pestañas: Buzón CRM, Inventario, Respaldos GIT)
│
├── static/                     # Archivos estáticos fuente
│   ├── app.js                  # Frontend Vanilla JS (Catálogo, Carrito, Búsqueda, Modales, CRM, Git)
│   ├── style.css               # Hoja de estilos de lujo responsive con variables CSS
│   └── logo.png                # Logotipo del sitio
│
├── staticfiles/                # Archivos estáticos compilados recolectados por collectstatic para WhiteNoise
├── productos/                  # Directorio local donde se guardan las fotos subidas de los productos
├── db.sqlite3                  # Base de datos relacional SQLite
├── servidor_produccion.py      # Script servidor Waitress multi-hilo configurado para Windows
├── requirements.txt            # Dependencias con versiones fijadas (Django, waitress, whitenoise, pillow...)
├── .env.example                # Plantilla de variables de entorno
└── .gitignore                  # Configurado para ignorar .env, logs y cachés
```

---

## 4. BITÁCORA DE PROBLEMAS CRÍTICOS RESUELTOS (KNOWLEDGE BASE)

A lo largo del proyecto se resolvieron problemas de ingeniería muy específicos que **deben tenerse en cuenta para no reintroducirlos**:

### 1. Bloqueo de Base de Datos SQLite en Windows durante Restauraciones Git
* **Síntoma:** Al restaurar una versión con `git checkout`, Git fallaba con `unable to unlink db.sqlite3: Permission denied` (Exit status 128 o 1).
* **Causa:** El servidor de producción Waitress / Django mantiene un descriptor de archivo abierto hacia `db.sqlite3`. En el sistema de archivos NTFS de Windows, un archivo bloqueado no puede ser reemplazado por otro proceso.
* **Solución definitiva en `git_service.py`:**
  Se invoca `django.db.connections.close_all()` inmediatamente antes de ejecutar el checkout de Git para liberar todos los handles del archivo en el sistema operativo, junto con un mecanismo de respaldo binario directo en caso de emergencia.

### 2. Broken Pipe / Exit Status 141 en Subprocesos de Git
* **Síntoma:** Los comandos de `git commit` o `git status` disparados desde la web fallaban con código 141 o rompían el worker de Waitress.
* **Causa:** Waitress en segundo plano corre en una consola no interactiva. Cuando un proceso hijo de Git escribe en `stdout` o `stderr` sin que haya una tubería asignada, el sistema operativo genera un error de pipe roto.
* **Solución definitiva en `git_service.py`:**
  Se creó la función centralizada `_git_run(*args)` que siempre ejecuta `subprocess.run(capture_output=True, text=True, encoding='utf-8')`.

### 3. Fallo de Commit cuando no hay cambios pendientes
* **Síntoma:** Si el usuario hacía clic en "Crear Copia GIT" sin haber modificado productos ni fotos, Git devolvía `exit status 1` indicando *"nothing to commit"*.
* **Solución:** `git_service.py` comprueba `git status --porcelain`. Si no hay cambios, automáticamente ejecuta `git commit --allow-empty -m "... (Sin cambios)"`, permitiendo continuar la secuencia correlativa de versiones sin fallar.

### 4. Bloqueo de Consola de Windows por Codificación de Caracteres (`cp1252`)
* **Síntoma:** Imprimir emojis Unicode (como 🚀 o 💾) en `servidor_produccion.py` hacía que Python 3.14 en Windows lanzara un `UnicodeEncodeError: 'charmap' codec can't encode character`.
* **Solución:** Se estandarizaron todos los mensajes de consola de los scripts de servidor a texto ASCII limpio.

### 5. Eliminación de Dependencia Externa Inútil (jQuery)
* **Auditoría:** En `index.html` se cargaba jQuery desde la CDN de Google para una función huérfana `CatAction` que no se usaba. Todo el frontend (`app.js`) está escrito en Vanilla JS puro. Se eliminó la etiqueta de script, ahorrando peticiones de red y render-blocking time.

---

## 5. COMANDOS OPERATIVOS FRECUENTES

### Iniciar Servidores:
```powershell
# Producción con Waitress (Puerto 8080):
python servidor_produccion.py

# Desarrollo con Django (Puerto 8000):
python manage.py runserver 0.0.0.0:8000
```

### Compilar Archivos Estáticos tras Modificar CSS/JS:
```powershell
python manage.py collectstatic --noinput
```

### Crear Respaldo Manual en Git desde Consola:
```powershell
python -c "import os, django; os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'LuxuryMonsei.settings'); django.setup(); from modelos.services.git_service import create_backup; print(create_backup('Nota de respaldo'))"
```

---

## 6. LA PLANTILLA DE MARCA BLANCA (`PLANTILLA_ECOMMERCE`)

Ubicada en: `c:\Users\Carlos Enyerve\Desktop\PROYECTOS\PLANTILLA_ECOMMERCE`

* Creada como boilerplate independiente de marca blanca.
* Contiene logos y 5 imágenes placeholder en `productos/` (800x800 px).
* Su base de datos viene inicializada con textos universales (`[ NOMBRE DE TU MARCA ]`), PIN `1234`, usuario `admin` / `admin1234`.
* Posee su propio manual de personalización: [`GUIA_DE_PERSONALIZACION.md`](GUIA_DE_PERSONALIZACION.md).
* Tiene su propio Git inicializado en `v1.0.0`, listo para conectarse a cualquier cuenta de GitHub.

---

## 7. PROTOCOLO DE RECUPERACIÓN TRAS FORMATEO DE PC

Si la computadora es formateada:
1. Instalar **Python 3.10+** (marcando indispensablemente `"Add python.exe to PATH"`).
2. Instalar **Git for Windows**.
3. Descomprimir el archivo `RESPALDO_COMPLETO_PROYECTOS.zip`:
   * Colocar la carpeta `PROYECTOS` en el Escritorio.
   * Colocar los archivos de `CONFIGURACION_SSH_GITHUB/` en `C:\Users\<Usuario>\.ssh\`.
4. Abrir terminal en `PROYECTOS\MET` e instalar requerimientos:
   ```bash
   pip install -r requirements.txt
   ```
5. Iniciar con `python servidor_produccion.py`.
6. Al abrir esta conversación con el asistente IA, enviar este archivo o escribir:  
   *"Asistente, lee el archivo HISTORIAL_Y_MEMORIA_PROYECTO.md de mi proyecto MET y continuemos trabajando."*
