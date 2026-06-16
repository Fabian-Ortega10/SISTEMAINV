from django.contrib import admin
from .models import MovimientoContable

@admin.register(MovimientoContable)
class MovimientoContableAdmin(admin.ModelAdmin):
    list_display = ('tipo', 'descripcion', 'monto', 'fecha')
    list_filter = ('tipo', 'fecha')
    search_fields = ('descripcion',)


