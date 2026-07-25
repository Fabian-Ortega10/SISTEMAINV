# admin.py
from django.contrib import admin
from .models import Categoria, Producto

@admin.register(Categoria)
class CategoriaAdmin(admin.ModelAdmin):
    list_display = ('nombre', 'descripcion')

@admin.register(Producto)
class ProductoAdmin(admin.ModelAdmin):
    # Reemplazamos 'precio' por tus campos reales: precio_costo y precio_venta
    list_display = ('nombre', 'categoria', 'precio_costo', 'precio_venta', 'ganancia_unitaria', 'stock')
    list_filter = ('categoria',)
    search_fields = ('nombre',)

