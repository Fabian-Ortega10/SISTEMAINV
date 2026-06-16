from django.urls import path
from .views import (
    VentaListView,
    VentaCreateView,
    VentaUpdateView,
    VentaDeleteView,
    DetalleVentaListView,
    ClienteListView,
    ClienteCreateView,
    ClienteUpdateView,
    ClienteDeleteView,
    exportar_ventas_csv,
)

app_name = "ventas"

urlpatterns = [
    # Ventas
    path('', VentaListView.as_view(), name='venta_list'),
    path('nuevo/', VentaCreateView.as_view(), name='venta_create'),
    path('<int:pk>/editar/', VentaUpdateView.as_view(), name='venta_update'),
    path('<int:pk>/eliminar/', VentaDeleteView.as_view(), name='venta_delete'),
    path('detalles/', DetalleVentaListView.as_view(), name='detalleventa_list'),

    # Clientes
    path('clientes/', ClienteListView.as_view(), name='cliente_list'),
    path('clientes/nuevo/', ClienteCreateView.as_view(), name='cliente_create'),
    path('clientes/<int:pk>/editar/', ClienteUpdateView.as_view(), name='cliente_update'),
    path('clientes/<int:pk>/eliminar/', ClienteDeleteView.as_view(), name='cliente_delete'),

    # Exportación CSV
    path('exportar/csv/', exportar_ventas_csv, name='exportar_csv'),
]