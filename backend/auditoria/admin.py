from django.contrib import admin
from .models import RegistroAuditoria

@admin.register(RegistroAuditoria)
class RegistroAuditoriaAdmin(admin.ModelAdmin):
    list_display = ('fecha', 'accion', 'modelo', 'objeto_id', 'usuario')
    list_filter = ('accion', 'modelo', 'fecha')
    search_fields = ('detalle',)

