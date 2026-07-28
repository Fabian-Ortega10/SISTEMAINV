from decimal import Decimal

from django.core.exceptions import ValidationError
from django.db import transaction

from contabilidad.models import MovimientoContable
from inventario.models import Producto


class StockInsuficienteError(ValidationError):
    """Se lanza cuando no hay stock suficiente para una operación."""


def _ajustar_stock(producto_id: int, delta: int) -> Producto:
    """Bloquea la fila del producto y ajusta stock de forma atómica."""
    producto = Producto.objects.select_for_update().get(pk=producto_id)
    nuevo_stock = producto.stock + delta
    if nuevo_stock < 0:
        raise StockInsuficienteError(
            f"Stock insuficiente para '{producto.nombre}'. "
            f"Disponible: {producto.stock}, solicitado: {abs(delta)}."
        )
    producto.stock = nuevo_stock
    producto.save(update_fields=["stock"])
    return producto


def _registrar_movimiento(tipo: str, descripcion: str, monto: Decimal) -> None:
    MovimientoContable.objects.create(
        tipo=tipo,
        descripcion=descripcion,
        monto=monto,
    )


# ── Compras ──────────────────────────────────────────────────────────────────

@transaction.atomic
def procesar_detalle_compra(detalle) -> None:
    """
    Al crear un DetalleCompra: aumenta stock y registra egreso contable.
    Usa precio_unitario del detalle (el precio real pactado con el proveedor),
    NO el precio_costo del producto, para mayor precisión contable.
    """
    producto = _ajustar_stock(detalle.producto_id, detalle.cantidad)
    monto = detalle.cantidad * detalle.precio_unitario
    _registrar_movimiento(
        tipo="EGRESO",
        descripcion=(
            f"Compra: {detalle.cantidad} x {producto.nombre} "
            f"(Orden #{detalle.orden_id})"
        ),
        monto=monto,
    )


@transaction.atomic
def revertir_detalle_compra(detalle) -> None:
    """Al eliminar un DetalleCompra: revierte stock y egreso."""
    producto = _ajustar_stock(detalle.producto_id, -detalle.cantidad)
    monto = detalle.cantidad * detalle.precio_unitario
    _registrar_movimiento(
        tipo="INGRESO",
        descripcion=(
            f"Reversión compra: {detalle.cantidad} x {producto.nombre} "
            f"(Orden #{detalle.orden_id})"
        ),
        monto=monto,
    )


# ── Ventas ───────────────────────────────────────────────────────────────────

@transaction.atomic
def procesar_detalle_venta(detalle) -> None:
    """
    Al crear un DetalleVenta: disminuye stock y registra ingreso contable.
    Usa precio_unitario del detalle (precio_venta al momento de la venta).
    """
    producto = _ajustar_stock(detalle.producto_id, -detalle.cantidad)
    monto = detalle.cantidad * detalle.precio_unitario
    _registrar_movimiento(
        tipo="INGRESO",
        descripcion=(
            f"Venta: {detalle.cantidad} x {producto.nombre} "
            f"(Venta #{detalle.venta_id})"
        ),
        monto=monto,
    )


@transaction.atomic
def revertir_detalle_venta(detalle) -> None:
    """Al eliminar un DetalleVenta: revierte stock e ingreso."""
    producto = _ajustar_stock(detalle.producto_id, detalle.cantidad)
    monto = detalle.cantidad * detalle.precio_unitario
    _registrar_movimiento(
        tipo="EGRESO",
        descripcion=(
            f"Reversión venta: {detalle.cantidad} x {producto.nombre} "
            f"(Venta #{detalle.venta_id})"
        ),
        monto=monto,
    )


# ── Producción ──────────────────────────────────────────────────────────────

@transaction.atomic
def finalizar_orden_produccion(orden) -> None:
    """
    Al finalizar una OrdenProduccion:
    - Descuenta stock de cada ConsumoMateriaPrima usando precio_costo
      del producto (costo real de la materia prima consumida).
    - Aumenta stock de cada ProductoFinal usando precio_costo
      del producto terminado generado.
    """
    # 1. Descontar materias primas → EGRESO al precio_costo
    for consumo in orden.consumomateriaprima_set.select_related("producto"):
        producto = _ajustar_stock(consumo.producto_id, -consumo.cantidad)
        # Usar precio_costo: refleja el costo real de la materia prima consumida
        monto = consumo.cantidad * producto.precio_costo
        _registrar_movimiento(
            tipo="EGRESO",
            descripcion=(
                f"Producción: consumo {consumo.cantidad} x {producto.nombre} "
                f"(Orden Prod. #{orden.id})"
            ),
            monto=monto,
        )

    # 2. Agregar productos finales → INGRESO al precio_costo del terminado
    for final in orden.productofinal_set.select_related("producto"):
        producto = _ajustar_stock(final.producto_id, final.cantidad)
        # Usar precio_costo: representa el valor de producción, no el precio de venta
        monto = final.cantidad * producto.precio_costo
        _registrar_movimiento(
            tipo="INGRESO",
            descripcion=(
                f"Producción: ingreso {final.cantidad} x {producto.nombre} "
                f"(Orden Prod. #{orden.id})"
            ),
            monto=monto,
        )