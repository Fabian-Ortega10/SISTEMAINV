from django.db import models
from inventario.models import Producto


class Proveedor(models.Model):
    nombre = models.CharField(max_length=150, unique=True)
    contacto = models.CharField(max_length=150, blank=True, null=True)
    telefono = models.CharField(max_length=50, blank=True, null=True)
    direccion = models.TextField(blank=True, null=True)

    class Meta:
        verbose_name = "Proveedor"
        verbose_name_plural = "Proveedores"
        ordering = ["nombre"]

    def __str__(self):
        return self.nombre


class OrdenCompra(models.Model):

    class EstadoCompra(models.TextChoices):
        PENDIENTE  = "PENDIENTE",  "Pendiente"
        RECIBIDA   = "RECIBIDA",   "Recibida"
        CANCELADA  = "CANCELADA",  "Cancelada"

    proveedor = models.ForeignKey(Proveedor, on_delete=models.CASCADE)
    fecha = models.DateField(auto_now_add=True)
    estado = models.CharField(
        max_length=10,
        choices=EstadoCompra.choices,
        default=EstadoCompra.PENDIENTE,
        verbose_name="Estado de la orden",
    )

    class Meta:
        verbose_name = "Orden de compra"
        verbose_name_plural = "Órdenes de compra"
        ordering = ["-fecha"]

    def __str__(self):
        return f"Orden #{self.id} - {self.proveedor} [{self.get_estado_display()}]"

    def get_total(self):
        return sum(
            d.precio_unitario * d.cantidad
            for d in self.detalles.all()
        )

    @property
    def es_cancelada(self):
        return self.estado == self.EstadoCompra.CANCELADA

    @property
    def es_recibida(self):
        return self.estado == self.EstadoCompra.RECIBIDA


class DetalleCompra(models.Model):
    orden = models.ForeignKey(OrdenCompra, on_delete=models.CASCADE, related_name="detalles")
    producto = models.ForeignKey(Producto, on_delete=models.CASCADE)
    cantidad = models.PositiveIntegerField()
    precio_unitario = models.DecimalField(max_digits=10, decimal_places=2)

    class Meta:
        verbose_name = "Detalle de compra"
        verbose_name_plural = "Detalles de compra"

    def __str__(self):
        return f"{self.cantidad} x {self.producto.nombre}"

    def save(self, *args, **kwargs):
        """
        El stock solo se actualiza cuando la orden pasa a RECIBIDA.
        Si la orden está PENDIENTE o CANCELADA, no se toca el inventario.
        La lógica de transición la maneja OrdenCompraUpdateView.
        """
        es_nuevo = self.pk is None
        super().save(*args, **kwargs)
        # Solo procesar stock si la orden ya está RECIBIDA al momento
        # de guardar el detalle (caso: agregar línea a orden ya recibida)
        if es_nuevo and self.orden.es_recibida:
            from core.services.inventario import procesar_detalle_compra
            procesar_detalle_compra(self)

    def delete(self, *args, **kwargs):
        # Solo revertir stock si la orden estaba RECIBIDA
        if self.orden.es_recibida:
            from core.services.inventario import revertir_detalle_compra
            revertir_detalle_compra(self)
        super().delete(*args, **kwargs)
