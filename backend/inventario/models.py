from django.db import models


class Categoria(models.Model):
    nombre = models.CharField(max_length=100, unique=True)
    descripcion = models.TextField(blank=True, null=True)

    class Meta:
        verbose_name = "Categoría"
        verbose_name_plural = "Categorías"
        ordering = ["nombre"]

    def __str__(self):
        return self.nombre


class Producto(models.Model):

    class UnidadMedida(models.TextChoices):
        UNIDAD   = "UND", "Unidad"
        PAR      = "PAR", "Par"
        METRO    = "MET", "Metro"
        YARDA    = "YRD", "Yarda"
        ROLLO    = "ROL", "Rollo"
        LITRO    = "LIT", "Litro"
        GALON    = "GAL", "Galón"
        KILOGRAM = "KGR", "Kilogramo"
        DOCENA   = "DOC", "Docena"

    class TipoProducto(models.TextChoices):
        MATERIA_PRIMA      = "MP", "Materia Prima"
        PRODUCTO_TERMINADO = "PT", "Producto Terminado"

    nombre = models.CharField(max_length=150)
    categoria = models.ForeignKey(
        Categoria,
        on_delete=models.CASCADE,
        related_name="productos",
    )
    tipo = models.CharField(
        max_length=2,
        choices=TipoProducto.choices,
        default=TipoProducto.MATERIA_PRIMA,
        verbose_name="Tipo de producto",
    )
    # --- Mejora 3: precio separado en costo y venta ---
    precio_costo = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=0,
        verbose_name="Precio de costo",
        help_text="Costo de producción o compra al proveedor.",
    )
    precio_venta = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=0,
        verbose_name="Precio de venta",
        help_text="Precio que se cobra al cliente.",
    )
    stock = models.PositiveIntegerField(default=0)
    unidad_medida = models.CharField(
        max_length=3,
        choices=UnidadMedida.choices,
        default=UnidadMedida.UNIDAD,
        verbose_name="Unidad de medida",
    )
    descripcion = models.TextField(blank=True, null=True)

    class Meta:
        verbose_name = "Producto"
        verbose_name_plural = "Productos"
        ordering = ["nombre"]

    def __str__(self):
        return f"{self.nombre} ({self.get_tipo_display()})"

    @property
    def margen_ganancia(self):
        """
        Retorna el margen de ganancia en porcentaje.
        Ejemplo: costo=50, venta=80 → margen=60%
        Devuelve None si precio_costo es 0 para evitar división por cero.
        """
        if not self.precio_costo:
            return None
        margen = ((self.precio_venta - self.precio_costo) / self.precio_costo) * 100
        return round(margen, 2)

    @property
    def ganancia_unitaria(self):
        """Diferencia absoluta entre precio de venta y costo."""
        return self.precio_venta - self.precio_costo