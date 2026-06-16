"""
Registra los signals al arrancar la aplicación mediante ready().
Sin esto, los handlers en signals.py nunca se conectan.
"""
 
from django.apps import AppConfig
 
 
class AuditoriaConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "auditoria"
 
    def ready(self):
        # El import de signals.py ejecuta el código de registro de handlers.
        # No se usa la variable — solo el efecto de importar el módulo.
        import auditoria.signals  # noqa: F401