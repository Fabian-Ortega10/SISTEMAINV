import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'sistemainv.settings')
django.setup()

from django.contrib.auth import get_user_model

User = get_user_model()

# Django leerá estos datos desde la configuración oculta de Render
username = os.environ.get('SUPERUSER_NAME', 'fabian')
email = os.environ.get('SUPERUSER_EMAIL', 'fabian@admin.com')
password = os.environ.get('SUPERUSER_PASSWORD')

if password:
    if not User.objects.filter(username=username).exists():
        print("Creando superusuario seguro para Render...")
        User.objects.create_superuser(username=username, email=email, password=password)
        print("¡Superusuario seguro creado con éxito!")
    else:
        print("El superusuario ya existe en la base de datos de Render.")
else:
    print("Error: No se encontró la variable SUPERUSER_PASSWORD en el servidor.")
