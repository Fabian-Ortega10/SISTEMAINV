from django.db import models

class RegistroAuditoria(models.Model):
    accion = models.CharField(max_length=100)  # Ej: CREAR, ACTUALIZAR, ELIMINAR
    modelo = models.CharField(max_length=100)  # Nombre del modelo afectado
    objeto_id = models.PositiveIntegerField()  # ID del objeto afectado
    usuario = models.CharField(max_length=150, blank=True, null=True)  # opcional
    fecha = models.DateTimeField(auto_now_add=True)
    detalle = models.TextField(blank=True, null=True)

    def __str__(self):
        return f"{self.fecha} - {self.accion} {self.modelo} ({self.objeto_id})"

