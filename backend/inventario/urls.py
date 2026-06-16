from django.urls import path
from .views import (
    ProductoListView,
    ProductoCreateView,
    ProductoUpdateView,
    ProductoDeleteView,
    CategoriaListView,
    CategoriaCreateView,
    CategoriaUpdateView,
    CategoriaDeleteView,
    exportar_inventario_csv,
)

app_name = "inventario"

urlpatterns = [
    path('', ProductoListView.as_view(), name='producto_list'),
    path('nuevo/', ProductoCreateView.as_view(), name='inventario_create'),
    path('<int:pk>/editar/', ProductoUpdateView.as_view(), name='inventario_update'),
    path('<int:pk>/eliminar/', ProductoDeleteView.as_view(), name='inventario_delete'),

    path('categorias/', CategoriaListView.as_view(), name='categoria_list'),
    path('categorias/nuevo/', CategoriaCreateView.as_view(), name='categoria_create'),
    path('categorias/<int:pk>/editar/', CategoriaUpdateView.as_view(), name='categoria_update'),
    path('categorias/<int:pk>/eliminar/', CategoriaDeleteView.as_view(), name='categoria_delete'),

    # Exportación CSV
    path('exportar/csv/', exportar_inventario_csv, name='exportar_csv'),
]
