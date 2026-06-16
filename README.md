# SISTEMAINV

> Sistema ERP para gestión integral de una zapatería — desarrollado en **Django 6 + PostgreSQL**.

---

## Descripción

SISTEMAINV es un sistema de gestión empresarial (ERP) diseñado específicamente para zapaterías. Cubre el ciclo completo del negocio: desde la compra de materias primas, pasando por la producción, hasta la venta del producto terminado — con trazabilidad completa, control de stock en tiempo real y registro contable automático.

---

## Módulos implementados

### Inventario
- CRUD completo de productos y categorías
- Control de stock en tiempo real
- Alertas de stock bajo en el dashboard
- Exportación a CSV

### Compras
- Registro de órdenes de compra con líneas de detalle (formulario inline)
- CRUD de proveedores
- Actualización automática de stock al registrar una compra
- Generación automática de egreso contable
- Exportación a CSV

### Ventas
- Registro de ventas con líneas de detalle (formulario inline)
- CRUD de clientes
- Disminución automática de stock al registrar una venta
- Generación automática de ingreso contable
- Cálculo de total por venta
- Exportación a CSV

### Producción
- Registro de órdenes de producción con materias primas consumidas y productos finales
- Flujo controlado: la orden se planea en estado **Pendiente** sin afectar stock
- Al **Finalizar** la orden: descuenta materias primas, aumenta productos terminados y registra movimientos contables automáticamente
- Validación de stock insuficiente con reversión automática
- Órdenes finalizadas bloqueadas para evitar duplicación de movimientos

### Contabilidad
- Registro automático de ingresos y egresos desde ventas, compras y producción
- Vista de balance con total de ingresos, egresos y saldo
- Registro manual de movimientos adicionales

### Auditoría
- Historial automático de todas las acciones (CREAR, ACTUALIZAR, ELIMINAR)
- Implementado con **Django Signals** — completamente desacoplado de los modelos
- Captura el usuario de sesión en cada registro via middleware

### Dashboard
- KPIs en tiempo real: productos en inventario, ventas del día, órdenes de producción pendientes, balance actual
- Alertas visuales de stock bajo (≤ 5 unidades)
- Últimas 5 ventas registradas
- Accesos rápidos a las acciones más frecuentes

### Autenticación y roles
- Login/logout propio (independiente del admin de Django)
- Sistema de roles con permisos granulares por módulo:

| Rol | Acceso |
|---|---|
| **Admin** | Acceso completo a todos los módulos |
| **Vendedor** | Inventario y Ventas |
| **Inventarista** | Inventario y Compras |
| **Contador** | Contabilidad |
| **Auditor** | Auditoría |

---

## Stack tecnológico

| Tecnología | Uso |
|---|---|
| Python 3.12 | Lenguaje principal |
| Django 6 | Framework web |
| PostgreSQL | Base de datos |
| Bootstrap 5 | Interfaz de usuario |
| WhiteNoise | Archivos estáticos en producción |
| python-dotenv | Variables de entorno |
| dj-database-url | Configuración de BD en Render |
| Render.com | Despliegue en la nube |

---

## Instalación local

### 1. Clona el repositorio
```bash
git clone https://github.com/Fabian-Ortega10/SISTEMAINV.git
cd SISTEMAINV
```

### 2. Crea y activa el entorno virtual
```bash
python -m venv .venv
.venv\Scripts\activate        # Windows
source .venv/bin/activate     # Linux/Mac
```

### 3. Instala las dependencias
```bash
pip install -r requirements.txt
```

### 4. Configura las variables de entorno
Crea un archivo `.env` en la carpeta `backend/` (junto a `manage.py`):

```env
SECRET_KEY=tu_clave_secreta_larga_y_aleatoria
DEBUG=True

DB_NAME=sistemainv
DB_USER=tu_usuario_postgres
DB_PASSWORD=tu_contraseña_postgres
DB_HOST=localhost
DB_PORT=5432
```

Para generar una `SECRET_KEY` segura:
```bash
python -c "import secrets; print(secrets.token_urlsafe(60))"
```

### 5. Aplica las migraciones
```bash
cd backend
python manage.py migrate
```

### 6. Crea el superusuario
```bash
python manage.py createsuperuser
```

### 7. Crea los roles del sistema
```bash
python manage.py crear_roles
```

### 8. Levanta el servidor
```bash
python manage.py runserver
```

Accede en: `http://127.0.0.1:8000`

---

## ☁️ Despliegue en Render

El proyecto está configurado para desplegarse en [Render.com](https://render.com).

Variables de entorno a configurar en el panel de Render:

```
SECRET_KEY=tu_clave_secreta
DEBUG=False
DATABASE_URL=postgresql://...  (la provee Render automáticamente)
```

---

## Estructura del proyecto

```
SISTEMAINV/
├── .gitignore
├── README.md
├── requirements.txt
├── LICENSE
└── backend/
    ├── manage.py
    ├── .env                  ← NO se sube a git
    ├── sistemainv/           ← Configuración del proyecto
    │   ├── settings.py
    │   ├── urls.py
    │   └── views.py          ← Dashboard
    ├── core/
    │   └── services/
    │       └── inventario.py ← Lógica de stock y contabilidad
    ├── inventario/
    ├── compras/
    ├── ventas/
    ├── produccion/
    ├── contabilidad/
    ├── auditoria/
    │   ├── signals.py        ← Auditoría automática
    │   └── middleware.py     ← Captura usuario de sesión
    ├── templates/
    │   ├── base.html
    │   ├── dashboard.html
    │   └── registration/
    │       └── login.html
    └── static/
        └── css/
            └── styles.css
```

---

## Flujo del negocio

```
Compra de materias primas
        ↓
  Stock aumenta automáticamente
  Egreso contable registrado
        ↓
  Orden de producción (Pendiente)
  Planear consumos y productos finales
        ↓
  Finalizar orden de producción
  Materias primas descontadas
  Productos terminados aumentados
  Movimientos contables registrados
        ↓
  Venta del producto terminado
  Stock disminuye automáticamente
  Ingreso contable registrado
        ↓
  Dashboard → KPIs en tiempo real
  Balance → Ingresos vs Egresos
```

---

## Licencia

Este proyecto está bajo la licencia incluida en el archivo `LICENSE`.