SISTEMAINV
Sistema de Inventarios desarrollado en Python con Django y PostgreSQL.
El sistema está diseñado para gestionar productos, compras, ventas, contabilidad y auditoría, ofreciendo una solución modular, escalable y con trazabilidad completa.

1. Características principales
Inventario: CRUD de categorías y productos, control de stock y precios.

Compras: registro de órdenes de compra, asociación con proveedores, actualización automática de stock y generación de egresos contables.

Ventas: registro de ventas, disminución de stock, generación de comprobantes/facturas y creación de ingresos contables.

Contabilidad: registro automático de ingresos y egresos, cálculo de balance y flujo de caja mediante comandos de gestión.

Auditoría: historial de acciones de usuarios y trazabilidad de cambios en compras y ventas.

Reportes: listados y exportación en formatos estándar (CSV, PDF), además de comandos personalizados (python manage.py reporte_contable).

Roles y permisos: sistema de grupos con permisos específicos:
    Admin → acceso completo.
    Vendedor → acceso a Inventario y Ventas.
    Inventarista → acceso a Inventario y Compras.
    Contador → acceso a Contabilidad.
    Auditor → acceso a Auditoría.

2. Requerimientos previos
Python 3.x

Django

PostgreSQL

Git

Entorno virtual (venv)

3. Instalación y configuración
Clona el repositorio:
git clone https://github.com/Fabian-Ortega10/SISTEMAINV.git
cd SISTEMAINV

Crea y activa el entorno virtual:
python -m venv .venv
source .venv/bin/activate   # Linux/Mac
.venv\Scripts\activate      # Windows

Instala las dependencias:
pip install -r requirements.txt

Configura la base de datos en backend/sistemainv/settings.py.
Para PostgreSQL: define usuario, contraseña, host y puerto.

Aplica migraciones:
python manage.py migrate

Crea un superusuario:
python manage.py createsuperuser

Levanta el servidor:
python manage.py runserver
Accede al panel de administración en:
http://127.0.0.1:8000/admin/

4. Casos de uso principales
CRUD de productos y categorías en inventario.

Registro de compras → stock aumenta, se genera egreso contable y registro de auditoría.

Registro de ventas → stock disminuye, se genera ingreso contable y registro de auditoría.

Auditoría → historial de acciones de usuarios.

Reportes → generación de balance y flujo de caja con:
python manage.py reporte_contable

5. Estructura del proyecto
SISTEMAINV/
│── .gitignore
│── README.md
│── requirements.txt
│── LICENSE
│── backend/
    │── manage.py
    │── sistemainv/
    │── inventario/
    │── compras/
    │── ventas/
    │── contabilidad/
    │   └── management/
    │       └── commands/
    │           └── reporte_contable.py
    │── auditoria/

6. Estado actual
Inventario, Compras, Ventas, Contabilidad y Auditoría implementados y funcionando en Django Admin.

Superusuario creado y acceso al panel de administración operativo.

Reporte contable básico disponible vía comando de gestión.

Repositorio en GitHub con documentación organizada y profesional.

7. Licencia
Este proyecto está bajo la licencia incluida en el archivo LICENSE.

8. Arquitectura del Sistema:
   https://copilot.microsoft.com/th/id/BCO.028fbc03-b47a-4792-b5e5-6424472861d2.png
El sistema SISTEMAINV está organizado en módulos independientes que se comunican entre sí, garantizando escalabilidad y trazabilidad:

Inventario
Productos
Categorías
Compras
Órdenes de compra
Proveedores
Ventas
Registro de ventas
Facturación
Contabilidad
Movimientos contables
Balance y reportes
Auditoría
Registros de auditoría
Trazabilidad de cambios

1. Roles y permisos
El sistema implementa control de acceso basado en grupos:
    Admin → acceso completo a todos los módulos.
    Inventarista → acceso a Inventario y Compras.
    Vendedor → acceso a Inventario y Ventas.
    Contador → acceso a Contabilidad.
    Auditor → acceso a Auditoría.