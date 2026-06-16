"""
Almacena el usuario del request en una variable local al hilo (thread-local)
para que los signals de auditoría puedan acceder a él sin necesitar el request.
 
Patrón estándar en Django para pasar contexto a capas que no reciben request.
"""
 
import threading
 
_thread_local = threading.local()
 
 
class AuditoriaMiddleware:
    """
    Captura request.user y lo guarda en thread-local al inicio de cada request.
    Limpia el valor al finalizar para evitar fugas entre requests.
 
    Registro en settings.py:
        MIDDLEWARE = [
            ...
            'auditoria.middleware.AuditoriaMiddleware',  # ← añadir al final
        ]
    """
 
    def __init__(self, get_response):
        self.get_response = get_response
 
    def __call__(self, request):
        _thread_local.current_user = getattr(request, "user", None)
        try:
            response = self.get_response(request)
        finally:
            # Limpieza garantizada incluso si la vista lanza excepción
            _thread_local.current_user = None
        return response
 
 
def get_current_user():
    """
    Retorna el usuario del request activo en el hilo actual.
    Retorna None si se llama fuera del ciclo de un request
    (ej. desde un management command o celery task).
    """
    return getattr(_thread_local, "current_user", None)