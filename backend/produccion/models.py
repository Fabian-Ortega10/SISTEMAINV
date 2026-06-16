from django.db import models
from inventario.models import Producto


class OrdenProduccion(models.Model):
    fecha = models.DateField(auto_now_add=True)
    descripcion = models.TextField()
    estado = models.CharField(
        max_length=20,
        choices=[("PENDIENTE", "Pendiente"), ("FINALIZADA", "Finalizada")],
        default="PENDIENTE",
    )
    # Marca de control: se llena la primera vez que la orden se finaliza.
    # Evita que finalizar_orden_produccion() se ejecute dos veces sobre la
    # misma orden (lo que duplicaría movimientos de stock/contabilidad).
    finalizada_en = models.DateTimeField(null=True, blank=True)

    class Meta:
        verbose_name = "Orden de producción"
        verbose_name_plural = "Órdenes de producción"
        ordering = ["-fecha"]

    def __str__(self):
        return f"Orden {self.id} - {self.estado}"

    @property
    def ya_finalizada(self) -> bool:
        return self.finalizada_en is not None


class ConsumoMateriaPrima(models.Model):
    orden = models.ForeignKey(OrdenProduccion, on_delete=models.CASCADE)
    producto = models.ForeignKey(Producto, on_delete=models.CASCADE)  # materia prima
    cantidad = models.PositiveIntegerField()

    class Meta:
        verbose_name = "Consumo de materia prima"
        verbose_name_plural = "Consumos de materia prima"

    def __str__(self):
        return f"{self.cantidad} x {self.producto.nombre} (Orden #{self.orden_id})"


class ProductoFinal(models.Model):
    orden = models.ForeignKey(OrdenProduccion, on_delete=models.CASCADE)
    producto = models.ForeignKey(Producto, on_delete=models.CASCADE)  # zapato terminado
    cantidad = models.PositiveIntegerField()

    class Meta:
        verbose_name = "Producto final"
        verbose_name_plural = "Productos finales"

    def __str__(self):
        return f"{self.cantidad} x {self.producto.nombre} (Orden #{self.orden_id})"