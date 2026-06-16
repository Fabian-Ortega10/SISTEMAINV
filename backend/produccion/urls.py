from django.urls import path
from .views import (
    OrdenProduccionListView,
    OrdenProduccionCreateView,
    OrdenProduccionUpdateView,
    OrdenProduccionDeleteView,
)

app_name = "produccion"

urlpatterns = [
    # Lista de órdenes de producción
    path('', OrdenProduccionListView.as_view(), name='ordenproduccion_list'),

    # Crear nueva orden de producción
    path('nuevo/', OrdenProduccionCreateView.as_view(), name='ordenproduccion_create'),

    # Editar orden de producción
    path('<int:pk>/editar/', OrdenProduccionUpdateView.as_view(), name='ordenproduccion_update'),

    # Eliminar orden de producción
    path('<int:pk>/eliminar/', OrdenProduccionDeleteView.as_view(), name='ordenproduccion_delete'),
]
