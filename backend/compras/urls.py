from django.urls import path
from .views import (
    OrdenCompraListView,
    OrdenCompraCreateView,
    OrdenCompraUpdateView,
    OrdenCompraDeleteView,
    DetalleCompraListView,
    ProveedorListView,
    ProveedorCreateView,
    ProveedorUpdateView,
    ProveedorDeleteView,
    exportar_compras_csv,
)

app_name = "compras"

urlpatterns = [
    # Órdenes de compra
    path('', OrdenCompraListView.as_view(), name='ordencompra_list'),
    path('nuevo/', OrdenCompraCreateView.as_view(), name='ordencompra_create'),
    path('<int:pk>/editar/', OrdenCompraUpdateView.as_view(), name='ordencompra_update'),
    path('<int:pk>/eliminar/', OrdenCompraDeleteView.as_view(), name='ordencompra_delete'),
    path('detalles/', DetalleCompraListView.as_view(), name='detallecompra_list'),

    # Proveedores
    path('proveedores/', ProveedorListView.as_view(), name='proveedor_list'),
    path('proveedores/nuevo/', ProveedorCreateView.as_view(), name='proveedor_create'),
    path('proveedores/<int:pk>/editar/', ProveedorUpdateView.as_view(), name='proveedor_update'),
    path('proveedores/<int:pk>/eliminar/', ProveedorDeleteView.as_view(), name='proveedor_delete'),

    # Exportación CSV
    path('exportar/csv/', exportar_compras_csv, name='exportar_csv'),
]