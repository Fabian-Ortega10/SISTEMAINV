from django.db import models

class MovimientoContable(models.Model):
    TIPOS = (
        ("INGRESO", "Ingreso"),
        ("EGRESO", "Egreso"),
    )
    tipo = models.CharField(max_length=10, choices=TIPOS)
    descripcion = models.TextField()
    monto = models.DecimalField(max_digits=12, decimal_places=2)
    fecha = models.DateField(auto_now_add=True)

    def __str__(self):
        return f"{self.tipo} - {self.monto} ({self.fecha})"
