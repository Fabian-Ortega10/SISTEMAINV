# SISTEMAINV

Sistema de Inventarios desarrollado en **Python** con **Django** y **PostgreSQL**.  
El sistema está diseñado para gestionar productos, compras, ventas, contabilidad y auditoría, ofreciendo una solución modular y escalable.

---

## Características principales

- **Inventario**: CRUD de categorías y productos, control de stock y precios.  
- **Compras**: registro de órdenes de compra, asociación con proveedores y actualización automática de stock.  
- **Ventas**: registro de ventas, disminución de stock, generación de comprobantes/facturas.  
- **Contabilidad**: registro de ingresos y egresos, reportes financieros básicos.  
- **Auditoría**: historial de acciones de usuarios y trazabilidad de cambios.  
- **Reportes**: listados y exportación en formatos estándar (CSV, PDF).  

---

## Requerimientos previos

- Python 3.x  
- Django  
- PostgreSQL (o SQLite para pruebas locales)  
- Git  
- Entorno virtual (`venv`)  

---

## ⚙️ Instalación y configuración

1. Clona el repositorio:
   ```bash
   git clone https://github.com/Fabian-Ortega10/SISTEMAINV.git
   cd SISTEMAINV

2. Crea y activa el entorno virtual:
   python -m venv .venv
source .venv/bin/activate   # Linux/Mac
.venv\Scripts\activate      # Windows

3. Instala las dependencias:
pip install -r requirements.txt

4. Configura la base de datos en backend/sistemainv/settings.py.

Para PostgreSQL: define usuario, contraseña, host y puerto.

5. Aplica migraciones:
python manage.py migrate

6. Crea un superusuario:
   python manage.py createsuperuser

7. Levanta el servidor:
   python manage.py runserver
Accede al panel de administración en:
http://127.0.0.1:8000/admin/ (127.0.0.1 in Bing)

8. Casos de uso principales
Administrador crea superusuario y gestiona roles.

CRUD de productos y categorías en inventario.

Registro de compras → stock aumenta y se refleja en contabilidad.

Registro de ventas → stock disminuye y se refleja en contabilidad.

Auditoría → historial de acciones de usuarios.

Generación de reportes de inventario, compras, ventas y contabilidad.

9. Estructura del proyecto
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
    │── auditoria/


10. Estado actual
Inventario implementado y funcionando en Django Admin.

Superusuario creado y acceso al panel.

Repositorio en GitHub con documentación inicial.

Próximos pasos: implementar módulos de Compras, luego Ventas, Contabilidad y Auditoría.

11. Licencia
Este proyecto está bajo la licencia incluida en el archivo LICENSE.


---

 Con este README tu repositorio quedará **profesional y completo**.  

¿Quieres que te prepare también un **.gitignore recomendado para Django + PostgreSQL** para que lo subas junto con el README y evites archivos innecesarios en GitHub?